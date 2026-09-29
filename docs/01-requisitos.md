# 1. Levantamento de Requisitos

**Sistema:** Sistema de Planos Didáticos — CEFET-MG
**Contexto:** Gestão administrativa de planos didáticos por período letivo, sem custo financeiro.

> **Análise do modelo existente**: a partir do estudo do plano didático "Plano-Didatico-v2023_LabPW.docx" (disciplina Laboratório de Programação Web), identificou-se estrutura com campos institucionais padronizados (carga horária, coordenador, departamento, período) e campos variáveis específicos por professor (atividades avaliativas, cronograma, metodologia, recursos). Esse modelo é a referência para os campos configuráveis do sistema.
>
> **Fluxo por semestre**: Coordenador define o período letivo, importa professores do sistema de RH, atribui professores às disciplinas, e então os Professores preenchem seus planos didáticos para aquele semestre. Coordenador visualiza e monitora a entrega dos planos.

## Requisitos Funcionais (RF)

| ID | Descrição | Prioridade | Ator/Origem |
|----|-----------|-----------|-------------|
| RF01 | Sistema deve permitir que professores submetam planos didáticos com campos configuráveis | Alta | Coordenador de Curso |
| RF02 | Sistema deve armazenar planos didáticos no banco de dados PostgreSQL | Alta | Coordenador de Curso |
| RF03 | Sistema deve gerar PDF do plano didático submetido | Média | Professor |
| RF04 | Admin deve poder criar/editar campos configuráveis do formulário | Alta | Administrador |
| RF05 | Coordenador deve visualizar lista de planos submetidos por professor | Média | Coordenador |
| RF06 | Sistema deve enviar lembretes automáticos para documentos não entregues | Média | Sistema |
| RF07 | Coordenador deve poder importar lista de professores (CSV/API) | Alta | Coordenador |
| RF08 | Coordenador deve poder gerenciar dados dos professores | Média | Coordenador |
| RF09 | Coordenador deve poder definir período letivo (ano/semestre) | Alta | Coordenador |
| RF10 | Coordenador deve poder atribuir professores às disciplinas por período letivo | Alta | Coordenador |
| RF11 | Sistema deve validar que o total de minutos (dias letivos × minutos_por_dia_letivo) seja ≥ carga horária da disciplina | Alta | Coordenador |
| RF12 | Sistema deve notificar atrasos na entrega de planos didáticos via e-mail (SMTP) e Telegram (canais configuráveis por destinatário) | Média | Sistema |

## Requisitos Não Funcionais (RNF)

| ID | Descrição | Prioridade | Ator/Origem |
|----|-----------|-----------|-------------|
| RNF01 | Sistema deve ser 100% gratuito (zero investimento financeiro) | Crítica | Universidade |
| RNF02 | API deve ser type-safe com FastAPI + PostgreSQL | Alta | Coordenador |
| RNF03 | Frontend Next.js deve ser responsivo e acessível | Alta | Professor |
| RNF04 | Dados devem persistir entre sessões | Alta | Coordenador |
| RNF05 | Sistema deve suportar múltiplos professores simultâneos | Média | Administrador |
| RNF06 | Sistema deve manter histórico de períodos letivos anteriores | Média | Coordenador |

## Rastreabilidade

Cada RF acima alimenta diretamente um ou mais casos de uso na seção 2 (`docs/02-casos-de-uso.md`). RNFs de persistência (RNF04, RNF06) decidem quais entidades são persistentes na seção 3 (`docs/03-diagrama-classes.md`); RNF01/RNF02/RNF03 restringem a stack tecnológica adotada na seção 10 (`docs/10-implementacao-ddd-clean-tdd.md`).

**Stack proposta:** FastAPI + PostgreSQL + Next.js + Python + SQLAlchemy + Alembic + Docker. Para RF12, o serviço de notificação adota o padrão Strategy com duas implementações concretas — `EmailSmtpNotifier` (biblioteca `aiosmtplib` ou `smtplib`) e `TelegramNotifier` (HTTP à `https://api.telegram.org/bot<token>/sendMessage`) — atrás da interface `INotifier`, permitindo adicionar novos canais (Slack, SMS, push) sem alterar o use case.
