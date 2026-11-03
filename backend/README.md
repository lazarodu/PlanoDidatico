# Backend - Sistema de Planos Didáticos

API FastAPI do sistema de planos didáticos do CEFET-MG.

## Configuração

As variáveis de ambiente estão documentadas em [`.env.example`](.env.example).
Para carregá-las em um console local:

```bash
set -a
source .env
set +a
```

O envio de e-mail usa, por padrão, a API HTTP do Resend ou do Brevo
(`EMAIL_PROVIDER` + `EMAIL_API_KEY`). O SMTP continua disponível como fallback,
mas é bloqueado no plano Free do Render.

## Testes

```bash
pip install -e ".[dev]"
pytest -q
```
