# 3. Diagrama de Classes

Classes extraídas dos substantivos dos requisitos (seção 1) e casos de uso (seção 2).

```mermaid
classDiagram
    class Usuario {
        -id: int
        -nome: str
        -email: str
        -tipo: str "admin/coordenador/professor"
        +eh_admin(): bool
        +eh_coordenador(): bool
        +eh_professor(): bool
        +pode_gerenciar_campos_formulario(): bool
        +pode_importar_campos_fixos(): bool
        +pode_preencher_campos_variaveis(): bool
    }

    class CampoFormulario {
        -id: int
        -nome: str
        -tipo: str "text/select/textarea/date"
        -obrigatorio: bool
        -ordem: int
    }

    class DidacticPlan {
        -id: int
        -professor_id: int
        -disciplina_id: int
        -periodo_letivo_id: int
        -status: str "submetido/validado/reprovado"
        -campos: JSON
        +gerar_pdf(): bytes
        +esta_pendente(): bool
        +marcar_como_entregue(): void
        +verificar_atraso(hoje: date): bool
        +get_status(): str
    }

    class ConfiguracaoCampo {
        -id: int
        -nome: str
        -tipo: str
        -obrigatorio: bool
    }

    class Professor {
        -usuario_id: int
        -departamento: str
        -matricula: str
    }

    class Disciplina {
        -id: int
        -codigo: str
        -nome: str
        -carga_horaria: int
        -natureza: str
        -area_formacao: str
        -departamento: str
    }

class PeriodoLetivo {
        -id: int
        -ano: int
        -semestre: int
        -ativo: bool
        -dataInicio: date
        -dataFim: date
        -data_limite_entrega_plano: date
        -minutos_por_dia_letivo: int "padrão 100"
        +get_minutos_por_dia_letivo(): int
        +get_data_limite_entrega_plano(): date
        +calcular_carga_horaria_minima(dias_letivos: List[DiaLetivoDisciplina]): int
        +validar_plano_entregue_no_prazo(data_entrega: date): bool
    }

    class AtribuicaoProfessorDisciplina {
        -id: int
        -professor_id: int
        -disciplina_id: int
        -periodo_letivo_id: int
        -horario: str
        +adicionar_dia_letivo(dia: DiaLetivoDisciplina): void
        +remover_dia_letivo(dia_id: int): void
        +validar_carga_horaria_suficiente(carga_horaria_disciplina: int) -> bool
    }

    class DiaLetivoDisciplina {
        -id: int
        -atribuicao_id: int
        -data: date
        -turno: str "matutino/vespertino/noturno"
        +get_minutos_contribuicao(periodo_minutos: int): int
    }

    class Notificador {
        <<interface>>
        +enviar(destinatario, mensagem): void
    }

    class EmailSmtpNotifier {
        -host: str
        -port: int
        -usuario: str
        -senha: str
        -from_addr: str
        +enviar(destinatario, mensagem): void
    }

    class TelegramNotifier {
        -bot_token: str
        +enviar(destinatario, mensagem): void
    }

    class NotificationPreference {
        -id: int
        -usuario_id: int
        -canal_email: bool
        -canal_telegram: bool
        -chat_id_telegram: str
        -horario_preferido: time
        +ativar_canal_email(): void
        +desativar_canal_email(): void
        +ativar_canal_telegram(chat_id: str): void
        +desativar_canal_telegram(): void
        +pode_receber_via_email(): bool
        +pode_receber_via_telegram(): bool
        +get_chat_id_telegram(): str?
    }

    class NotificationLog {
        -id: int
        -usuario_id: int
        -atribuicao_id: int
        -canal: str "email/telegram"
        -status: str "SENT/FAIL_NO_CHANNEL/FAIL_RETRY/SUCCESS"
        -mensagem_erro: str
        -criado_em: datetime
        +registrar(canal, destinatario, mensagem, status, erro=None): void
    }

    Usuario "1" -- "1" Professor : "eh"
    Usuario "1" -- "0..*" DidacticPlan : "submete"
    DidacticPlan "1" -- "0..*" CampoFormulario : "usa"
    Usuario "1" -- "0..*" CampoFormulario : "cria (Admin)"
    Usuario "1" -- "0..*" ConfiguracaoCampo : "gerencia (Admin)"
    Usuario "1" -- "0..*" Disciplina : "importa/gerencia (Coordenador)"
    Usuario "1" -- "0..*" PeriodoLetivo : "define (Coordenador)"
    Usuario "1" -- "0..*" AtribuicaoProfessorDisciplina : "atribui (Coordenador)"
    Usuario "1" -- "0..*" DiaLetivoDisciplina : "cadastra (Coordenador)"
    Disciplina "1" -- "0..*" DidacticPlan : "possui"
    PeriodoLetivo "1" -- "0..*" DidacticPlan : "contextualiza"
    PeriodoLetivo "1" -- "0..*" AtribuicaoProfessorDisciplina : "define"
    Professor "1" -- "0..*" AtribuicaoProfessorDisciplina : "tem"
    Disciplina "1" -- "0..*" AtribuicaoProfessorDisciplina : "recebe"
    AtribuicaoProfessorDisciplina "1" *-- "0..*" DiaLetivoDisciplina : "compõe"

    Usuario "1" -- "0..1" NotificationPreference : "tem"
    AtribuicaoProfessorDisciplina "1" -- "0..*" NotificationLog : "gera"
    Notificador <|.. EmailSmtpNotifier : "implementa"
    Notificador <|.. TelegramNotifier : "implementa"

    note for DidacticPlan "campos armazenados como JSON flexível\nComportamento: esta_pendente(), marcar_como_entregue(), verificar_atraso(hoje)"
    note for Usuario "Admin pode alterar/cadastrar campos\nCoordenador importa campos fixos\nProfessor preenche campos variáveis\ndiscriminador tipo: admin > coordenador > professor\nPermissões: pode_gerenciar_campos_formulario(), pode_importar_campos_fixos(), pode_preencher_campos_variaveis()"
    note for PeriodoLetivo "data_limite_entrega_plano: data de entrega padrão para todos os planos\nminutos_por_dia_letivo: padrão 100, configurável"
    note for DiaLetivoDisciplina "RF11: dias x minutos/dia >= carga_horaria da disciplina"
    note for Notificador <<interface>> INOTIFIER (port): Strategy de canal de notificação. Permite trocar/estender SMTP/Telegram sem alterar use case"
    note for EmailSmtpNotifier "RF12: envio assíncrono (aiosmtplib) com TLS"
    note for TelegramNotifier "RF12: POST https://api.telegram.org/bot<token>/sendMessage"
    note for NotificationLog "auditoria: cada tentativa (sucesso/falha) é registrada com timestamp para debug e anti-spam"
```

## Relações

- **Herança/hierarquia de perfil**: `Usuario.tipo` discrimina admin/coordenador/professor (herança lógica, sem hierarquia de tabelas).
- **Composição**: `AtribuicaoProfessorDisciplina *-- DiaLetivoDisciplina` — dia letivo não existe sem a atribuição.
- **Associação simples**: demais relações (Usuario–DidacticPlan, Disciplina–DidacticPlan, PeriodoLetivo–DidacticPlan etc.), com multiplicidade indicada em cada extremidade.

## Persistência

| Classe | Persistente? | Estratégia | Observação |
|--------|-------------|-----------|------------|
| Usuario | Sim | Tabela `usuario`, PK id | Discriminador `tipo` com hierarquia: admin > coordenador > professor |
| DidacticPlan | Sim | Tabela `didactic_plans`, PK id | FK → usuario_id, disciplina_id, periodo_letivo_id |
| CampoFormulario | Sim | Tabela `campo_formulario`, PK id | Admin gerencia, Coordenador importa |
| ConfiguracaoCampo | Sim | Tabela `configuracao_campo`, PK id | Campos do formulário (variáveis) |
| Professor | Sim | Tabela `professor`, PK usuario_id (FK Usuario) | Dados específicos do professor |
| Disciplina | Sim | Tabela `disciplina`, PK id | Importada do sistema acadêmico |
| PeriodoLetivo | Sim | Tabela `periodo_letivo`, PK id | Inclui data_limite_entrega_plano e minutos_por_dia_letivo |
| AtribuicaoProfessorDisciplina | Sim | Tabela `atribuicao_professor_disciplina`, PK id | Relacionamento N-N por período |
| DiaLetivoDisciplina | Sim | Tabela `dia_letivo_disciplina`, PK id | FK → atribuicao_id, contém data+turno |
| NotificationPreference | Sim | Tabela `notification_preference`, PK id; UNIQUE(usuario_id) | 0..1 por usuário; armazena canais ativos (e-mail/Telegram) e `chat_id` |
| NotificationLog | Sim | Tabela `notification_log`, PK id | Auditoria de cada tentativa (canal, status, erro, timestamp) |

Nenhuma classe candidata a valor não persistente (ex: enum embutido) além de `status` de `DidacticPlan` e `turno`/`tipo`, que ficam como coluna string com valores fixos (sem tabela própria).
