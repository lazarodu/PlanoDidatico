import pytest
from src.adapters.pdf_generator import PDFGeneratorAdapter
from src.adapters.notifiers.strategy_notifiers import EmailSmtpNotifier, TelegramNotifier

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
