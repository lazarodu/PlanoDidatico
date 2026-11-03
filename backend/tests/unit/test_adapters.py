import json

import httpx
import pytest

from src.adapters.pdf_generator import PDFGeneratorAdapter
from src.adapters.notifiers.strategy_notifiers import (
    EmailApiNotifier,
    EmailSmtpNotifier,
    TelegramNotifier,
    build_email_notifier,
)

@pytest.mark.asyncio
async def test_pdf_generator_adapter():
    pdf_bytes = PDFGeneratorAdapter.generate_plan_pdf(
        prof_nome="Prof. Dr. Roberto",
        disciplina_codigo="DECOM01",
        disciplina_nome="Laboratório de Web",
        periodo_str="2026/1",
        campos={"atividades_avaliativas": "Prova 1 (50%), Prova 2 (50%)", "cronograma": "Aula 1: Intro"}
    )
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")

@pytest.mark.asyncio
async def test_strategy_notifiers_simulated():
    email_notifier = EmailSmtpNotifier(hostname="localhost")
    res_email = await email_notifier.enviar("prof@cefet.br", "Teste de atraso", "Aviso")
    assert res_email is True

    telegram_notifier = TelegramNotifier(bot_token="dummy_token")
    res_tg = await telegram_notifier.enviar("12345678", "Teste de atraso", "Aviso")
    assert res_tg is True


def _mock_client(requests, status=200, payload=None):
    def handler(request):
        requests.append(request)
        return httpx.Response(
            status,
            json=payload if payload is not None else {"id": "email-123"},
        )

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


@pytest.mark.asyncio
async def test_email_api_notifier_resend():
    requests = []
    async with _mock_client(requests) as client:
        notifier = EmailApiNotifier(
            provider="resend",
            api_key="re_test",
            from_addr="no-reply@example.com",
            from_name="Planos",
            client=client,
        )
        assert await notifier.enviar("prof@cefet.br", "Teste", "Aviso") is True

    request = requests[0]
    assert str(request.url) == "https://api.resend.com/emails"
    assert request.headers["authorization"] == "Bearer re_test"
    assert json.loads(request.content) == {
        "from": "Planos <no-reply@example.com>",
        "to": ["prof@cefet.br"],
        "subject": "Aviso",
        "text": "Teste",
    }


@pytest.mark.asyncio
async def test_email_api_notifier_brevo():
    requests = []
    async with _mock_client(requests, status=201, payload={"messageId": "123"}) as client:
        notifier = EmailApiNotifier(
            provider="brevo",
            api_key="xkeysib-test",
            from_addr="no-reply@example.com",
            from_name="Planos",
            client=client,
        )
        assert await notifier.enviar("prof@cefet.br", "Teste", "Aviso") is True

    request = requests[0]
    assert str(request.url) == "https://api.brevo.com/v3/smtp/email"
    assert request.headers["api-key"] == "xkeysib-test"
    assert json.loads(request.content) == {
        "sender": {"name": "Planos", "email": "no-reply@example.com"},
        "to": [{"email": "prof@cefet.br"}],
        "subject": "Aviso",
        "textContent": "Teste",
    }


@pytest.mark.asyncio
async def test_email_api_notifier_returns_false_on_error():
    requests = []
    async with _mock_client(requests, status=422, payload={"message": "invalid"}) as client:
        notifier = EmailApiNotifier(provider="resend", api_key="re_test", client=client)
        assert await notifier.enviar("prof@cefet.br", "Teste") is False


@pytest.mark.asyncio
async def test_email_api_notifier_unknown_provider():
    notifier = EmailApiNotifier(provider="mailgun", api_key="key")
    assert await notifier.enviar("prof@cefet.br", "Teste") is False


@pytest.mark.asyncio
async def test_email_api_notifier_simulated_without_key():
    notifier = EmailApiNotifier(provider="resend", api_key="")
    assert await notifier.enviar("prof@cefet.br", "Teste") is True


def test_build_email_notifier_uses_api_when_key_is_set(monkeypatch):
    monkeypatch.setenv("EMAIL_API_KEY", "re_test")
    assert isinstance(build_email_notifier(), EmailApiNotifier)

    monkeypatch.delenv("EMAIL_API_KEY")
    assert isinstance(build_email_notifier(), EmailSmtpNotifier)
