# Deploy — Render (backend) + Vercel (frontend)

Este projeto usa um monorepo com:

- `backend/` — API FastAPI, publicada no **Render** via Docker.
- `frontend/` — Next.js 16, publicado na **Vercel**.
- `.github/workflows/ci-cd.yml` — pipeline de CI/CD no **GitHub Actions**.

## Visão geral do pipeline

```text
Pull request ──► testes do backend + testes/build do frontend
                         │
                         ▼
Push na main ──► testes passam ──► deploy do backend no Render
                              └──► deploy do frontend na Vercel
```

O deploy só acontece depois que **os dois jobs de CI passam**. Em pull requests
os testes rodam, mas nada é publicado.

Arquivos de infraestrutura adicionados:

| Arquivo | Função |
| --- | --- |
| `render.yaml` | Blueprint do Render: web service Docker + PostgreSQL |
| `backend/Dockerfile` | Imagem de produção da API |
| `backend/.dockerignore` | Reduz o contexto de build |
| `frontend/vercel.json` | Configuração do projeto Next.js na Vercel |
| `.github/workflows/ci-cd.yml` | Pipeline de testes e deploys |

---

## 1. Backend no Render

### 1.1 Criar o Blueprint

1. Acesse o [Render Dashboard](https://dashboard.render.com) e clique em **New → Blueprint**.
2. Conecte o repositório do GitHub e selecione o arquivo `render.yaml`.
3. O Render vai criar:
   - `planos-didaticos-api` — web service Docker, plano Free, health check em `/health`.
   - `planos-didaticos-db` — PostgreSQL 16, plano Free.
4. Quando solicitado, preencha `CORS_ORIGINS`. Pode colocar `http://localhost:3000`
   por enquanto e atualizar depois com a URL da Vercel.
5. Clique em **Apply**.

O blueprint já define `autoDeployTrigger: off`: o Render **não** faz deploy a cada
push. Quem dispara o deploy é o GitHub Actions, depois que os testes passam.

### 1.2 Configurar variáveis de ambiente

O `DATABASE_URL` é preenchido automaticamente pelo Render a partir do banco criado
pelo blueprint. As demais variáveis podem ser cadastradas em
**Service → Environment**:

| Variável | Descrição |
| --- | --- |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula. Ex.: `https://meu-projeto.vercel.app` |
| `EMAIL_PROVIDER` | Provedor HTTP de e-mail: `resend` ou `brevo` (padrão: `resend`) |
| `EMAIL_API_KEY` | Chave da API do provedor; sem ela o envio é simulado |
| `EMAIL_FROM` | Remetente verificado no provedor |
| `EMAIL_FROM_NAME` | Nome exibido no remetente |
| `SMTP_*` | Fallback SMTP (`HOST`, `PORT`, `USER`, `PASSWORD`, `FROM`); bloqueado no Free |
| `TELEGRAM_BOT_TOKEN` | Token do bot do Telegram |

> **Limitações do plano Free do Render**
> - O serviço web hiberna após 15 minutos sem tráfego; a primeira requisição
>   depois disso demora cerca de 1 minuto.
> - O PostgreSQL gratuito expira **30 dias após a criação**.
> - Apenas um PostgreSQL Free pode ficar ativo por workspace.
> - As portas SMTP `25`, `465` e `587` são bloqueadas; use a API HTTP de
>   e-mail descrita na seção 1.5.
> - O scheduler interno não é confiável em serviços que hibernam.
>
> Para um trabalho com prazo maior, considere um banco externo gratuito
> (Neon, Supabase) ou um plano pago.

### 1.3 Obter a URL e o Deploy Hook

Depois do primeiro deploy:

- URL da API: algo como `https://planos-didaticos-api.onrender.com`.
- Teste o health check:

```bash
curl https://planos-didaticos-api.onrender.com/health
# {"status":"ok"}
```

- Documentação interativa: `https://planos-didaticos-api.onrender.com/docs`.
- Em **Service → Settings → Deploy Hook**, copie a URL secreta. Ela será usada
  no secret `RENDER_DEPLOY_HOOK_URL` do GitHub.

### 1.4 Usar um banco externo (opcional)

Se não quiser usar o PostgreSQL Free do Render:

1. Remova o bloco `databases:` do `render.yaml`.
2. Troque o `DATABASE_URL` do serviço para `sync: false`:

```yaml
      - key: DATABASE_URL
        sync: false
```

3. Cadastre a URL do banco no Dashboard do Render.

O backend normaliza automaticamente URLs nos formatos `postgres://` e
`postgresql://` para `postgresql+asyncpg://`, incluindo a tradução de
`sslmode=require` para o parâmetro `ssl` do asyncpg.

### 1.5 Enviar e-mail no plano Free (API HTTP)

O plano Free do Render bloqueia as portas SMTP, então o backend usa uma API
HTTP de e-mail. O adaptador suporta **Resend** e **Brevo**:

| Provedor | Free tier | Endpoint usado |
| --- | --- | --- |
| Resend | 3.000 e-mails/mês (100/dia) | `https://api.resend.com/emails` |
| Brevo | 300 e-mails/dia | `https://api.brevo.com/v3/smtp/email` |

**Resend**

1. Crie uma conta em [resend.com](https://resend.com).
2. Verifique um domínio em **Domains**. Para testes, `onboarding@resend.dev`
   só entrega para o e-mail dono da conta.
3. Crie uma API key em **API Keys**.
4. No Render, cadastre:
   - `EMAIL_PROVIDER=resend`
   - `EMAIL_API_KEY=<sua chave>`
   - `EMAIL_FROM=<remetente verificado>` (ex.: `nao-responda@seudominio.com`)
   - `EMAIL_FROM_NAME=Planos Didáticos CEFET-MG`

**Brevo**

1. Crie uma conta em [brevo.com](https://www.brevo.com).
2. Verifique o remetente em **Senders, Domains & Dedicated IPs**.
3. Crie uma API key em **SMTP & API → API Keys** (v3).
4. No Render, cadastre:
   - `EMAIL_PROVIDER=brevo`
   - `EMAIL_API_KEY=<sua chave>`
   - `EMAIL_FROM=<remetente verificado>`
   - `EMAIL_FROM_NAME=Planos Didáticos CEFET-MG`

O backend escolhe a API HTTP quando `EMAIL_API_KEY` está preenchida. Se ela
estiver vazia, tenta SMTP; sem SMTP configurado, o envio é apenas simulado e
registrado no log.

> O remetente precisa estar verificado no provedor. Para enviar aos professores,
> verifique um domínio próprio e configure SPF/DKIM no provedor.

---

## 2. Frontend na Vercel

### 2.1 Importar o projeto

1. Acesse o [Vercel Dashboard](https://vercel.com/dashboard) e clique em
   **Add New → Project**.
2. Importe o repositório do GitHub.
3. Em **Root Directory**, selecione `frontend`.
4. O framework será detectado como **Next.js**. Mantenha os comandos padrão
   (`npm install` / `npm run build`).
5. Clique em **Deploy**.
6. Guarde a URL de produção, por exemplo `https://planos-didaticos.vercel.app`.

### 2.2 Desativar o deploy automático do Git

Como o deploy será feito pelo GitHub Actions via Vercel CLI, desative o deploy
automático para não criar duas publicações por push:

- **Project → Settings → Git → Disconnect** (ou configure um *Ignored Build Step*
  que sempre ignore o build).

Se preferir usar a integração nativa da Vercel, mantenha o Git conectado e
remova o job `deploy-frontend` do workflow. Nesse caso o deploy da Vercel
acontece automaticamente, mas **não** fica bloqueado pelos testes do GitHub.

### 2.3 Obter token e IDs do projeto

1. Crie um token em **Account Settings → Tokens → Create Token**.
   Guarde o valor para o secret `VERCEL_TOKEN`.
2. Na pasta `frontend`, rode:

```bash
cd frontend
npx vercel link
cat .vercel/project.json
```

O arquivo terá algo como:

```json
{
  "orgId": "team_xxxxxxxxxxxxxxxx",
  "projectId": "prj_xxxxxxxxxxxxxxxx"
}
```

Use esses valores nos secrets `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID`.

> Não faça commit da pasta `.vercel/`. Ela é local e contém apenas os IDs do
> projeto.

### 2.4 Variáveis de ambiente do frontend

O frontend atual usa persistência local (`localStorage`) e ainda não consome a
API. Quando a integração for implementada, cadastre em
**Project → Settings → Environment Variables**:

| Variável | Valor |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | URL pública do backend no Render |

Marque a variável para os ambientes **Production** e **Preview**.

---

## 3. Secrets no GitHub

No repositório, acesse **Settings → Secrets and variables → Actions** e crie:

| Secret | Como obter |
| --- | --- |
| `RENDER_DEPLOY_HOOK_URL` | Render → serviço → Settings → Deploy Hook |
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens |
| `VERCEL_ORG_ID` | `.vercel/project.json` ou Team Settings |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` ou Project Settings |

Opcionalmente, crie o environment `production` em **Settings → Environments**
para exigir aprovação manual antes dos deploys.

---

## 4. Como o pipeline funciona

O workflow `.github/workflows/ci-cd.yml` roda em:

- `pull_request` para `main` — apenas testes.
- `push` para `main` — testes e, se tudo passar, os dois deploys.
- `workflow_dispatch` — execução manual; na branch `main` também publica.

### Job `backend`

1. Instala Python 3.12 e as dependências (`pip install ".[dev]"`).
2. Roda `pytest -q` (23 testes, usando SQLite assíncrono em memória).
3. Valida o build da imagem Docker de produção.

### Job `frontend`

1. Instala Node.js 22 e as dependências com `npm ci`.
2. Roda `npm test`.
3. Roda `npm run build`.

### Job `deploy-backend`

1. Faz `POST` no Deploy Hook do Render com `ref=<commit testado>`.
2. O Render constrói o `backend/Dockerfile` e só considera o deploy concluído
   quando `/health` responde.
3. O ID do deploy aparece no resumo do job.

### Job `deploy-frontend`

1. `vercel pull` baixa as configurações e variáveis de produção.
2. `vercel build --prod` gera os artefatos.
3. `vercel deploy --prebuilt --prod` publica na Vercel.
4. A URL publicada aparece no resumo do job.

Os deploys de backend e frontend rodam em paralelo depois do CI.

---

## 5. Verificação após o primeiro deploy

1. **GitHub Actions**: confira se os quatro jobs ficaram verdes.
2. **Render**: em **Events**, veja o deploy iniciado pelo hook.
3. **Backend**:

```bash
curl https://SEU-SERVICO.onrender.com/health
curl -I https://SEU-SERVICO.onrender.com/docs
```

4. **Vercel**: abra a URL de produção e navegue pelas páginas `/`, `/campos`,
   `/atribuicoes` e `/planos/[id]`.

---

## 6. Rodando localmente

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Ou com Docker Compose (PostgreSQL + API):

```bash
docker compose up --build
```

### Frontend

```bash
cd frontend
npm ci
npm test
npm run build
npm run dev
```

---

## 7. Rollback

- **Render**: **Service → Events → Rollback**. No plano Free é possível voltar
  para os dois deploys anteriores.
- **Vercel**: **Project → Deployments → ⋯ → Promote/Rollback**.

---

## 8. Troubleshooting

| Sintoma | Causa provável / solução |
| --- | --- |
| Health check do Render falha | Veja os logs do serviço. Confirme o `DATABASE_URL` e se o banco não expirou. |
| API demora na primeira requisição | Serviço Free hibernou; aguarde ~1 minuto. |
| `401` no Deploy Hook | A URL foi regenerada. Atualize o secret `RENDER_DEPLOY_HOOK_URL`. |
| `403`/`404` na Vercel CLI | Confira `VERCEL_TOKEN`, `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID`. |
| Build da Vercel falha | Confirme **Root Directory = `frontend`** e Node.js 22.x nas configurações do projeto. |
| E-mail não é enviado no Render Free | A porta SMTP é bloqueada; configure `EMAIL_API_KEY` (seção 1.5) ou use um plano pago. |
| `401`/`403` no Resend ou Brevo | Confira `EMAIL_API_KEY` e se `EMAIL_FROM` está verificado no provedor. |
| E-mail entregue na caixa de spam | Verifique o domínio no provedor (SPF/DKIM) e use um remetente do próprio domínio. |
| `ModuleNotFoundError` no backend | Rode `pip install -e ".[dev]"` ou verifique se o `README.md` do backend existe (usado pelo `pyproject.toml`). |
| Testes de integração falham localmente | Eles usam SQLite em memória; confirme `aiosqlite` instalado via `pip install -e ".[dev]"`. |
