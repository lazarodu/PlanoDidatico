# Checklist Final do Documento

- [x] 1. Requisitos funcionais e não funcionais (tabela) — `01-requisitos.md`
- [x] 2. Diagrama de casos de uso com atores (+ herança de ator), include, extend — `02-casos-de-uso.md`
- [x] 3. Descrição textual dos casos de uso principais (pré/pós-condição, fluxos) — `02-casos-de-uso.md`
- [x] 4. Diagrama de classes com composição, agregação, herança e multiplicidades — `03-diagrama-classes.md`
- [x] 5. Marcação de persistência das entidades — `03-diagrama-classes.md`
- [x] 6. Diagrama entidade-relacionamento (DER) — `04-der.md`
- [x] 7. Diagrama de objetos (instância) validando cardinalidades/relações — `05-diagrama-objetos.md`
- [x] 8. Diagrama de estados — avaliado, aplicável a `DidacticPlan.status` — `06-diagrama-estados.md`
- [x] 9. Classes de fronteira/controle/entidade mapeadas por caso de uso — `07-boundary-control-entity.md`
- [x] 10. Diagrama de sequência dos casos de uso principais — `08-diagrama-sequencia.md`
- [x] 11. Diagrama(s) de atividade para os fluxos principais — `09-diagrama-atividades.md`
- [x] 12. Diagrama de componentes (camadas Clean Architecture) — `10-diagrama-componentes.md`
- [x] 13. Mapeamento DDD (aggregates, entidades, value objects, repositories) — `11-implementacao-ddd-clean-tdd.md`
- [x] 14. Estrutura de camadas Clean Architecture (domain/application/adapters/infra) — `11-implementacao-ddd-clean-tdd.md`
- [x] 15. Plano de testes TDD por caso de uso (unidade domínio → use case → integração) — `11-implementacao-ddd-clean-tdd.md`

## Rastreabilidade

- Cada RF (`01-requisitos.md`) aparece em pelo menos um caso de uso (`02-casos-de-uso.md`).
- Cada caso de uso relevante aparece na tabela boundary/control/entity (`07-boundary-control-entity.md`) e no diagrama de sequência (`08-diagrama-sequencia.md`).
- Cada entity aparece no diagrama de classes (`03-diagrama-classes.md`) e no DER (`04-der.md`).
- Cada caso de uso implementado tem teste de aceitação ligado ao RF de origem (`11-implementacao-ddd-clean-tdd.md`).

**Data da proposta:** 8 de setembro de 2026
**Projeto:** Sistema de Planos Didáticos — CEFET-MG, administrativo, sem custos financeiros
**Stack:** FastAPI + PostgreSQL + Next.js + Python + SQLAlchemy + Alembic + Docker
