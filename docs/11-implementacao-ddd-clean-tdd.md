# 10. Implementação: DDD, Clean Architecture, TDD

Depois do documento pronto (seções 1-9), usar como insumo direto para implementação. Ordem: domínio primeiro, depois aplicação, depois infra/interface. Nunca começar pelo banco ou pelo controller.

## DDD (Domain-Driven Design)

- **Entidade de domínio**: `DidacticPlan`, `AtribuicaoProfessorDisciplina`, `Usuario` — identidade própria, ciclo de vida, sem dependência de framework/ORM.
- **Value Object**: `CampoFormulario` (config de campo dinâmico), `DiaLetivo` (data+turno, imutável, comparado por valor).
- **Aggregate e Aggregate Root**: `AtribuicaoProfessorDisciplina` é raiz, `DiaLetivoDisciplina` só é acessado através dela (nunca referenciado direto de fora do agregado) — mesma composição já definida na seção 3.
- **Repository**: uma interface por aggregate root — `IDidacticPlanRepository`, `IAtribuicaoRepository`, `IUsuarioRepository`.
- **Domain Service**: `ValidadorCargaHoraria` — regra RF11 (`dias × minutos_por_dia_letivo ≥ carga_horaria`) não pertence só a `AtribuicaoProfessorDisciplina` nem só a `Disciplina`, envolve os dois aggregates.
- **Linguagem ubíqua**: nomes usados no requisito/caso de uso mantidos no código (`DidacticPlan`, `PeriodoLetivo`, `minutos_por_dia_letivo`) — nada de `Manager`/`Helper`/`Processor` genérico.

| Aggregate Root | Entidades internas | Value Objects | Repository |
|-----------------|--------------------|--------------|-------------|
| DidacticPlan | — | CampoFormulario | IDidacticPlanRepository |
| AtribuicaoProfessorDisciplina | DiaLetivoDisciplina | DiaLetivo | IAtribuicaoRepository |
| Usuario | Professor | — | IUsuarioRepository |
| PeriodoLetivo | — | — | IPeriodoLetivoRepository |

## Clean Architecture (camadas)

Mapeada direto da seção 6 (boundary/control/entity). Regra de dependência: camada externa depende da interna, nunca o contrário.

1. **Domain/Entities** — entidades e value objects DDD, sem dependência externa.
2. **Application/Use Cases** — 1 classe por caso de uso (`SubmissaoUseCase`, `AtribuicaoDisciplinasUseCase`, `GerenciaCamposUseCase`, `PeriodoLetivoUseCase`) = "Control" da seção 6.
3. **Interface Adapters** — controllers FastAPI, páginas Next.js (entrada); repositories SQLAlchemy (saída) = "Boundary" da seção 6.
4. **Frameworks & Drivers** — PostgreSQL, FastAPI, Next.js, ReportLab. Detalhe substituível.

### Estrutura de pastas proposta

```
src/
  domain/            <- entidades DDD, value objects, interfaces de repository
    entities/
      user.py
      didactic_plan.py
      atribuicao_professor_disciplina.py
    value_objects/
      field_config.py
      dia_letivo.py
    repositories/
      user_repository.py
      didactic_plan_repository.py
      atribuicao_repository.py
      notification_repository.py
    services/         <- ports (interfaces) - Clean Architecture
      notifier.py          # INotifier (port) - Strategy de canal
  application/        <- use cases
    use_cases/
      submit_didactic_plan.py
      manage_fields.py
      atribuir_professor_disciplina.py
      definir_periodo_letivo.py
      notify_delays.py     # DetectarAtrasosUseCase + ConfigurarCanaisUseCase
  adapters/
    controllers/       <- boundary de entrada (REST FastAPI)
      didactic_plan.py
      atribuicao.py
      notification.py      # endpoint admin: configurar canais; endpoint coordenador: disparar manualmente
    repositories/       <- implementação concreta
      sqlalchemy_didactic_plan.py
      sqlalchemy_user.py
      sqlalchemy_atribuicao.py
      sqlalchemy_notification.py
    notifiers/          <- adapters do port INotifier
      email_smtp_notifier.py    # aiosmtplib + TLS
      telegram_notifier.py      # httpx.AsyncClient → api.telegram.org
  infra/               <- config framework, ORM, conexão banco
    database.py
    security.py
    scheduler.py        # APScheduler: job diário "detectar_atrasos"
```

Regra prática de checagem: se importar lib de banco (ORM, driver SQL) dentro de arquivo de use case ou entidade → violação, mover para adapter/infra.

## TDD (Test-Driven Development)

Ciclo **red → green → refactor**, de dentro para fora (domínio → use case → adapter).

### Pirâmide de testes

1. **Testes Unitários de Domínio** (muito numerosos): entidade `DidacticPlan` (validação de campos, transições de status, geração de PDF); `ValidadorCargaHoraria` (regra RF11 com casos limite — exatamente igual, um minuto a menos).
2. **Testes de Use Case** (médios): `SubmissaoUseCase`, `AtribuicaoDisciplinasUseCase` usando fakes de repository em memória (nunca mockar entidade de domínio, só repository/gateway externo).
3. **Testes de Integração** (poucos): repository real contra SQLite/Postgres, mapeamento ORM.
4. **Testes E2E** (mínimos): Cypress/Playwright nos fluxos críticos do frontend (submissão de plano, atribuição de disciplina).

### RF → Caso de Uso → Teste de Aceitação

| RF | Caso de Uso | Teste de Aceitação |
|----|-------------|-------------------|
| RF01 | UC1 Submeter Plano Didático | Professor pode submeter plano com todos os campos |
| RF02 | UC1 (include: Salvar no Banco) | Dado persiste no PostgreSQL |
| RF03 | UC1 (extend: Gerar PDF) | PDF é gerado com conteúdo correto |
| RF04 | UC8 Gerenciar Campos | Admin pode criar novo campo de formulário |
| RF05 | UC7 Visualizar Planos | Coordenador visualiza lista de planos por professor |
| RF06 | UC1 (extend: Lembrete) | Sistema envia lembrete para plano não entregue |
| RF07 | UC11 Importar Professores | Coordenador importa lista de professores via CSV |
| RF08 | UC11 Gerenciar Professores | Coordenador edita dados de professor importado |
| RF09 | UC13 Definir Período Letivo | Coordenador cria período letivo com data_limite e minutos_por_dia_letivo |
| RF10 | UC12 Atribuir Professores | Coordenador atribui professor a disciplina por período |
| RF11 | UC14 Cadastrar Dias Letivos | Sistema valida que `dias × minutos_por_dia_letivo >= carga_horaria`, rejeitando atribuição insuficiente |
| RF12 | UC15 Notificar Atrasos (UC16 Configurar Canais) | Job diário detecta atraso e dispara `INotifier` para e-mail (SMTP) e/ou Telegram, registrando `NotificationLog`; falha de canal re-tenta com backoff e não bloqueia demais destinatários |

Cada RF da seção 1 tem pelo menos um teste de aceitação ligado — rastreabilidade completa RF → caso de uso → teste.
