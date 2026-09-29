# 3.1 Diagrama Entidade-Relacionamento (DER)

Derivado direto da tabela de persistência da seção 3: todas as classes marcadas `Persistente? = Sim` entram no DER. Enquanto o diagrama de classes mostra visão de objeto (composição, herança, comportamento), o DER mostra visão relacional: tabela, PK, FK e cardinalidade.

```mermaid
erDiagram
    USUARIO ||--o{ DIDACTIC_PLAN : "submete"
    USUARIO ||--|| PROFESSOR : "eh"
    USUARIO ||--o{ ATRIBUICAO_PROFESSOR_DISCIPLINA : "tem"
    USUARIO ||--o| NOTIFICATION_PREFERENCE : "configura"
    USUARIO ||--o{ NOTIFICATION_LOG : "recebe"
    DISCIPLINA ||--o{ DIDACTIC_PLAN : "possui"
    DISCIPLINA ||--o{ ATRIBUICAO_PROFESSOR_DISCIPLINA : "tem"
    PERIODO_LETIVO ||--o{ DIDACTIC_PLAN : "contextualiza"
    PERIODO_LETIVO ||--o{ ATRIBUICAO_PROFESSOR_DISCIPLINA : "define"
    ATRIBUICAO_PROFESSOR_DISCIPLINA ||--o{ DIA_LETIVO_DISCIPLINA : "tem"
    ATRIBUICAO_PROFESSOR_DISCIPLINA ||--o{ NOTIFICATION_LOG : "dispara"

    USUARIO {
        bigint id PK
        string nome
        string email
        string tipo "admin/coordenador/professor"
    }
    PROFESSOR {
        bigint usuario_id PK,FK
        string matricula
        string departamento
    }
    DISCIPLINA {
        bigint id PK
        string codigo
        string nome
        int carga_horaria
        string natureza
        string area_formacao
        string departamento
    }
    PERIODO_LETIVO {
        bigint id PK
        int ano
        int semestre
        bool ativo
        date data_inicio
        date data_fim
        date data_limite_entrega_plano
        int minutos_por_dia_letivo "padrão 100"
    }
    ATRIBUICAO_PROFESSOR_DISCIPLINA {
        bigint id PK
        bigint professor_id FK
        bigint disciplina_id FK
        bigint periodo_letivo_id FK
        string horario
    }
    DIA_LETIVO_DISCIPLINA {
        bigint id PK
        bigint atribuicao_id FK
        date data
        string turno "matutino/vespertino/noturno"
    }
    DIDACTIC_PLAN {
        bigint id PK
        bigint usuario_id FK
        bigint disciplina_id FK
        bigint periodo_letivo_id FK
        string status
        json campos
    }
    CAMPO_FORMULARIO {
        bigint id PK
        string nome
        string tipo
        bool obrigatorio
        int ordem
    }
    CONFIGURACAO_CAMPO {
        bigint id PK
        string nome
        string tipo
        bool obrigatorio
    }
    NOTIFICATION_PREFERENCE {
        bigint id PK
        bigint usuario_id FK,UK "1 por usuario"
        bool canal_email
        bool canal_telegram
        string chat_id_telegram
        time horario_preferido
    }
    NOTIFICATION_LOG {
        bigint id PK
        bigint usuario_id FK
        bigint atribuicao_id FK
        string canal "email/telegram"
        string status "SENT/FAIL_NO_CHANNEL/FAIL_RETRY/SUCCESS"
        string mensagem_erro
        datetime criado_em
    }
```

## Regras de conversão aplicadas

- **Herança de `Usuario`** (admin/coordenador/professor): estratégia de **tabela única com coluna discriminadora** `tipo` — evita duplicação de FK em `professor`, único caso onde subtipo carrega atributo próprio (matrícula, departamento), resolvido com tabela `professor` referenciando `usuario.id` 1:1.
- **Composição `AtribuicaoProfessorDisciplina *-- DiaLetivoDisciplina`** → FK `atribuicao_id` na tabela "muitos" (`dia_letivo_disciplina`), apontando para PK de `atribuicao_professor_disciplina`.
- **`CampoFormulario`/`ConfiguracaoCampo`**: tabelas próprias (não embutidas), pois são configuráveis dinamicamente por Admin/Coordenador — não são apenas enum fixo.
- **`DidacticPlan.campos`**: campo `json` (não normalizado) para suportar formulário dinâmico, conforme RNF de flexibilidade — decisão de modelagem documentada, não schema fixo.

Toda cardinalidade acima confere com a multiplicidade equivalente do diagrama de classes (`docs/03-diagrama-classes.md`).
