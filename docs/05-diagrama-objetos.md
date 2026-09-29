# 4. Diagrama de Objetos

Instantâneo do diagrama de classes em tempo de execução, usado para validar a regra RF11 (`dias letivos × minutos_por_dia_letivo ≥ carga_horaria`) e a composição `AtribuicaoProfessorDisciplina *-- DiaLetivoDisciplina` com um cenário concreto: disciplina "Laboratório de Programação Web" (carga horária 60h = 3600 min), período 2026.2, minutos por dia letivo padrão = 100.

```mermaid
classDiagram
    class periodo2026_2 {
        <<instance>>
        ano = 2026
        semestre = 2
        ativo = true
        data_limite_entrega_plano = 2026-08-15
        minutos_por_dia_letivo = 100
    }
    class disciplinaLPW {
        <<instance>>
        codigo = "SIN123"
        nome = "Laboratório de Programação Web"
        carga_horaria = 3600
    }
    class atribuicao1 {
        <<instance>>
        professor_id = 42
        disciplina_id = "SIN123"
        periodo_letivo_id = "2026.2"
    }
    class dia1 {
        <<instance>>
        data = 2026-08-03
        turno = "noturno"
    }
    class dia2 {
        <<instance>>
        data = 2026-08-10
        turno = "noturno"
    }
    class dia3 {
        <<instance>>
        data = 2026-08-17
        turno = "noturno"
    }

    periodo2026_2 --> atribuicao1
    disciplinaLPW --> atribuicao1
    atribuicao1 *-- dia1
    atribuicao1 *-- dia2
    atribuicao1 *-- dia3
```

## Validação demonstrada

- `atribuicao1` tem 3 dias letivos cadastrados (`dia1`, `dia2`, `dia3`) → `3 × 100 min = 300 min`.
- Se `disciplinaLPW.carga_horaria = 3600 min` (60h), esse cenário **falha** a regra RF11 (`300 < 3600`) — confirma que o total exigido de dias letivos para uma disciplina de 60h, a 100 min/dia, é de **36 dias letivos**, não 3. Esse número concreto é o que vira massa de teste na seção de TDD (`docs/11-implementacao-ddd-clean-tdd.md`): teste que rejeita atribuição com poucos dias e teste que aceita com 36+ dias.
- A composição `atribuicao1 *-- dia1/dia2/dia3` confirma que os dias letivos só existem enquanto a atribuição existir (exclusão em cascata ao remover a atribuição).
