# 8. Diagrama de Atividades

## Fluxo de Submissão de Plano Didático (UC1)

```mermaid
flowchart TD
    Start((Início)) --> A1[Professor acessa página de submissão]
    A1 --> A2[Sistema carrega campos configuráveis do banco]
    A2 --> D1{Todos campos obrigatórios preenchidos?}
    D1 -- Não --> A3[Mostrar erros de validação]
    A3 --> A2
    D1 -- Sim --> A4[Montar entidade DidacticPlan]
    A4 --> A5[Salvar no PostgreSQL via API]
    A5 --> A6[Gerar PDF usando ReportLab]
    A6 --> A7[Salvar PDF no banco ou armazenamento]
    A7 --> A8[Exibir confirmação ao professor]
    A8 --> Fim((Fim))
```

## Fluxo de Atribuição de Professor à Disciplina, com validação RF11 (UC12/UC14)

Raia Coordenador / Raia Sistema:

```mermaid
flowchart TD
    Start((Início)) --> B1[Coordenador seleciona período letivo]
    B1 --> B2[Coordenador seleciona professor e disciplina]
    B2 --> B3[Coordenador informa dias letivos data+turno]
    B3 --> B4[Sistema calcula total_minutos = dias x minutos_por_dia_letivo]
    B4 --> D1{total_minutos >= carga_horaria da disciplina?}
    D1 -- Não --> B5[Sistema exibe erro: carga horária insuficiente]
    B5 --> B3
    D1 -- Sim --> B6[Sistema salva atribuição e dias letivos]
    B6 --> B7[Sistema confirma atribuição ao coordenador]
    B7 --> Fim((Fim))
```

Raias: ações `B1/B2/B3` pertencem ao Coordenador; `B4/D1/B5/B6/B7` pertencem ao Sistema (backend de validação, RF11).
