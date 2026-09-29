# 2. Diagrama de Casos de Uso

## Distinção de Campos: Fixos vs Configuráveis

A arquitetura divide os campos do plano didático em duas categorias, com hierarquia de permissões definida.

### Campos Fixos (Institucionais — lidos do sistema acadêmico)

Importados do sistema acadêmico/RH, lidos por professores e coordenadores:

- **Campus/Curso**: nome do curso (ex: "Bacharelado em Sistemas de Informação")
- **Código da disciplina**: código oficial
- **Coordenador do curso**: nome do coordenador responsável
- **Nome da disciplina**: título específico
- **Docente responsável**: professor que submete
- **Carga horária total**: horas/aula e créditos
- **Natureza da disciplina**: prática/obrigatória
- **Área de formação DCN**: específica
- **Departamento que oferta**: nome do departamento
- **Cabeçalho institucional**: Ministério, CEFET-MG, Diretoria

### Campos Configuráveis (preenchidos pelo professor)

- Data de entrega
- Atividades avaliativas (tipos e descrições)
- Recursos utilizados (equipamentos, softwares, laboratórios)
- Cronograma detalhado (data e atividade de cada aula)
- Metodologia de ensino
- Observações
- Valores das atividades (percentuais de cada avaliação)

### Hierarquia de Permissões

| Perfil | Campos Fixos | Campos Variáveis | Gestão |
|--------|------------------------------|-----------------------------------|--------------------------|
| **Admin** | Criar/Editar/Configurar fontes | Criar/Editar/Configurar campos | Gerenciar sistema completo |
| **Coordenador** | Importar de sistemas externos + definir data de entrega e minutos por aula do período | Visualizar apenas | Importar/gerenciar professores, atribuir professores às disciplinas (por semestre), cadastrar dias letivos |
| **Professor** | Visualizar apenas | Editar/Preencher | Nenhuma |

**Implicação:** Admin > Coordenador > Professor. Professor também visualiza campos fixos importados pelo Coordenador. Admin gerencia tanto campos fixos (fontes de importação) quanto variáveis. Coordenador atua como gestor pedagógico a cada semestre: importa/atribui professores às disciplinas, define data de entrega padrão e minutos por dia letivo.

## Diagrama de Casos de Uso

```mermaid
flowchart LR
    Admin((Administrador))
    Coordenador((Coordenador))
    Professor((Professor))
    Admin -.generalização.-> Coordenador
    Coordenador -.generalização.-> Professor

    Professor --> UC1[Submeter Plano Didático]
    UC1 -.include.-> UC2[Validar Campos Obrigatórios]
    UC1 -.include.-> UC3[Salvar no Banco de Dados]
    UC1 -.extend.-> UC4[Gerar PDF do Plano]
    UC1 -.extend.-> UC5[Enviar Lembrete Automático]

    Coordenador --> UC6[Importar Campos Fixos]
    Coordenador --> UC7[Visualizar Planos de Professores]
    Coordenador --> UC11[Importar e Gerenciar Professores]
    Coordenador --> UC12[Atribuir Professores às Disciplinas]
    Coordenador --> UC13[Definir Período Letivo]
    Coordenador --> UC14[Cadastrar Dias Letivos]
    Coordenador --> UC15[Notificar Atrasos de Entrega]

    Admin --> UC8[Gerenciar Campos do Formulário]
    Admin --> UC9[Visualizar Todos os Planos]
    Admin --> UC10[Configurar Sistema]
    Admin --> UC16[Configurar Canais de Notificação]```

Elementos de notação: herança de ator (Admin herda de Coordenador, que herda de Professor — seta tracejada rotulada "generalização", já que Mermaid `flowchart` não tem símbolo nativo de triângulo de herança); `<<include>>` = comportamento sempre executado (validar campos, salvar no banco); `<<extend>>` = comportamento opcional (gerar PDF, lembrete automático).

**Relacionamentos extras (RF12 — notificação de atrasos):**
- `UC15` é disparado por um agendador (job diário) que detecta planos com `data_entrega < hoje` e `status != ENTREGUE`.
- A notificação é enviada por **e-mail (SMTP)** e/ou **Telegram**, conforme canais configurados em `UC16` por destinatário (professor ou coordenador).

## Casos de Uso Detalhados

**UC1 — Submeter Plano Didático**
- Ator: Professor
- Pré-condição: Professor está logado
- Fluxo principal: Professor visualiza campos fixos (importados) → Preenche campos variáveis → Clica em "Enviar" → Sistema salva no banco → Sistema gera PDF → Confirmação exibida
- Pós-condição: Plano didático registrado com data de entrega e campos preenchidos

**UC2 — Validar Campos Obrigatórios**
- Ator: Sistema (backend)
- Fluxo principal: Sistema verifica se todos os campos obrigatórios estão preenchidos antes de salvar
- Fluxo alternativo: Se campos faltam, retorna erros de validação para o frontend

**UC6 — Importar Campos Fixos**
- Ator: Coordenador
- Fluxo principal: Coordenador acessa painel → Sistema exibe dados importados do sistema acadêmico/RH → Coordenador confirma/atualiza valores → Campos fixos ficam disponíveis para os professores
- Pós-condição: Campos fixos sincronizados com os sistemas externos

**UC8 — Gerenciar Campos do Formulário**
- Ator: Administrador
- Fluxo principal: Admin acessa painel → Adiciona/remove/edita campos variáveis → Define tipos (text/select/textarea/date) → Define se obrigatório → Define ordem de exibição → Campos são salvos e passam a aparecer nos formulários dos professores

**UC11 — Importar e Gerenciar Professores**
- Ator: Coordenador
- Pré-condição: Coordenador logado, com acesso ao sistema acadêmico
- Fluxo principal: Coordenador acessa painel de gestão → Importa lista de professores do sistema de RH (CSV/API) → Sistema valida dados → Coordenador revisa/ajusta informações → Professores ficam disponíveis para atribuição
- Pós-condição: Base de professores atualizada no sistema para o semestre corrente

**UC12 — Atribuir Professores às Disciplinas**
- Ator: Coordenador
- Pré-condição: Professores e disciplinas já importados
- Fluxo principal: Coordenador seleciona semestre letivo → Lista disciplinas disponíveis → Atribui professor a cada disciplina → Informa dias letivos (data+turno) → Sistema valida que soma de minutos (dias × minutos_por_dia) ≥ carga horária → Salva atribuições
- Pós-condição: Professores vinculados às disciplinas do período, com cronograma letivo validado
- **Regra RF11**: para cada disciplina atribuída, `dias letivos × minutos_por_dia_letivo ≥ carga_horaria`. Coordenador define minutos por dia letivo (padrão: 100 min) na configuração do período.

**UC13 — Definir Período Letivo**
- Ator: Coordenador
- Fluxo principal: Coordenador define ano/semestre (ex: 2026.2) → Informa data de entrega padrão dos planos → Informa minutos por dia letivo (padrão: 100 min) → Sistema cria contexto do período → Professores veem apenas planos do período ativo → Histórico de períodos anteriores permanece acessível
- Pós-condição: Novo período letivo ativo, com data de entrega e minutos por dia letivo configurados
- Campos configuráveis do Período: `data_limite_entrega_plano` (data), `minutos_por_dia_letivo` (int, padrão 100)

**UC14 — Cadastrar Dias Letivos da Disciplina**
- Ator: Coordenador
- Pré-condição: Atribuição professor-disciplina já criada
- Fluxo principal: Coordenador seleciona atribuição → Cadastra dias letivos (data + turno: matutino/vespertino/noturno) → Sistema calcula total de minutos → Valida se total ≥ carga horária da disciplina → Salva dias letivos
- Pós-condição: Dias letivos cadastrados e validados para a disciplina no período
- **Regra RF11**: `SUM(dias letivos) × minutos_por_dia_letivo ≥ carga_horaria`

**UC15 — Notificar Atrasos de Entrega (RF12)**
- Ator: Sistema (job agendado) / Coordenador (disparo manual)
- Pré-condição: Período letivo ativo com `data_limite_entrega_plano` definida; canais de notificação configurados (UC16).
- Fluxo principal: Job diário (cron / APScheduler) executa `DetectarAtrasosUseCase` → Para cada atribuição com plano em status `PENDENTE` e `data_entrega < hoje`, monta payload (nome do professor, disciplina, dias de atraso, link do plano) → Resolve canais do destinatário (`e-mail`, `telegram` ou ambos) → Despacha via `INotifier` → `EmailSmtpNotifier` envia por SMTP (TLS) e `TelegramNotifier` chama `sendMessage` → Persiste registro em `NotificationLog` (canal, destinatário, status, erro) → Incrementa contador de reenvios respeitando intervalo mínimo configurável (default: 24 h)
- Fluxos alternativos:
  - 2a. Professor não tem canal cadastrado → registra `NotificationLog` com status `FAIL_NO_CHANNEL` e segue.
  - 2b. SMTP/Telegram falha (timeout, credencial inválida) → registra erro, marca tentativa e re-tenta no próximo ciclo (exponential backoff configurável).
  - 2c. Coordenador dispara manualmente via endpoint → confirma destinatários antes do envio.
- Pós-condição: Atraso registrado no histórico e destinatário notificado pelos canais habilitados.

**UC16 — Configurar Canais de Notificação (RF12)**
- Ator: Administrador (e-mail/Telegram globais) / Coordenador (preferências por destinatário)
- Pré-condição: Admin logado.
- Fluxo principal: Admin acessa painel → Define credenciais SMTP (host, porta, TLS, usuário, senha — armazenadas em vault/env) e/ou bot token do Telegram (via variável `TELEGRAM_BOT_TOKEN`) → Para cada destinatário, configura quais canais recebe (e-mail, telegram, ambos) e horário preferido de envio → Salva preferências em `NotificationPreference`
- Pós-condição: Canais ativos e prontos para serem consumidos por `UC15`.

**Regra RF12 — Canais suportados:**
| Canal | Tecnologia | Configuração |
|-------|-----------|--------------|
| E-mail | SMTP (TLS) via `aiosmtplib` | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` |
| Telegram | HTTP `POST https://api.telegram.org/bot{token}/sendMessage` | `TELEGRAM_BOT_TOKEN` + `chat_id` por destinatário |
