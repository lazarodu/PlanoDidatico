# 9. Diagrama de Componentes

Visão estrutural em módulos/pacotes, materializando as camadas de Clean Architecture (`docs/11-implementacao-ddd-clean-tdd.md`).

```mermaid
flowchart TB
    subgraph Adapters["Interface Adapters"]
        Controller[Router FastAPI]
        NextPage[Páginas Next.js]
        RepoImpl[SQLAlchemy Repositories]
        NotifImpl1[EmailSmtpNotifier]
        NotifImpl2[TelegramNotifier]
    end
    subgraph Application["Application"]
        UseCase[SubmissaoUseCase]
        UseCase2[AtribuicaoDisciplinasUseCase]
        UseCase3[GerenciaCamposUseCase]
        UseCase4[DetectarAtrasosUseCase]
    end
    subgraph Domain["Domain"]
        Entity[DidacticPlan «entity»]
        Entity2[AtribuicaoProfessorDisciplina «entity»]
        Entity3[NotificationPreference «entity»]
        Entity4[NotificationLog «entity»]
        ValueObj[CampoFormulario «value object»]
        RepoPort[[IDidacticPlanRepository «interface»]]
        RepoPort2[[IUsuarioRepository «interface»]]
        NotifPort[[INotifier «interface»]]
    end
    subgraph Infra["Frameworks & Drivers"]
        DB[(PostgreSQL)]
        FastAPI[FastAPI]
        Nextjs[Next.js]
        ReportLab[ReportLab - geração de PDF]
        SMTP[(Servidor SMTP externo)]
        TelegramAPI[Telegram Bot API]
        Scheduler[APScheduler - job diário]
    end

    Nextjs --> NextPage
    NextPage --> Controller
    Controller --> UseCase
    Controller --> UseCase2
    Controller --> UseCase3
    Controller --> UseCase4
    Scheduler --> UseCase4
    UseCase --> Entity
    UseCase --> RepoPort
    UseCase --> ReportLab
    UseCase2 --> Entity2
    UseCase2 --> RepoPort
    UseCase4 --> Entity2
    UseCase4 --> Entity3
    UseCase4 --> Entity4
    UseCase4 --> NotifPort
    RepoImpl -.implementa.-> RepoPort
    RepoImpl -.implementa.-> RepoPort2
    NotifImpl1 -.implementa.-> NotifPort
    NotifImpl2 -.implementa.-> NotifPort
    RepoImpl --> DB
    NotifImpl1 --> SMTP
    NotifImpl2 --> TelegramAPI
    Controller --> FastAPI
```

Regra de leitura: seta sempre aponta de quem depende para quem é dependido. `Domain` nunca depende de `Adapters`/`Infra` — só recebe, via interface implementada (`RepoPort`/`RepoPort2`).
