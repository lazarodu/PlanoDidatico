# 7. Diagrama de Sequência

## UC1 — Submeter Plano Didático

```mermaid
sequenceDiagram
    actor Professor
    participant Tela as TelaSubmissao «boundary»
    participant UseCase as SubmissaoUseCase «control»
    participant Entity as DidacticPlan «entity»
    participant Repository as DidacticPlanRepository
    participant Banco as PostgreSQL

    Professor ->> Tela: preenche formulário com campos configuráveis
    Professor ->> Tela: clica em "Enviar Plano"
    Tela ->> UseCase: submeter_plano(dados, usuario_id)
    UseCase ->> Entity: validar_campos_obrigatorios()
    alt campos válidos
        UseCase ->> Repository: salvar(entidade)
        Repository ->> Banco: INSERT INTO didactic_plans
        Banco -->> Repository: ok
        Repository -->> UseCase: ok
        UseCase ->> UseCase: gerar_pdf()
        UseCase -->> Tela: resposta_sucesso(com_pdf)
        Tela -->> Professor: mostra confirmação e link PDF
    else campos inválidos
        UseCase -->> Tela: erros_validacao
        Tela -->> Professor: exibe erros de validação
    end
```

## UC12 — Atribuir Professor à Disciplina (com validação RF11)

```mermaid
sequenceDiagram
    actor Coordenador
    participant Tela as TelaAtribuicaoDisciplinas «boundary»
    participant UseCase as AtribuicaoDisciplinasUseCase «control»
    participant Atrib as AtribuicaoProfessorDisciplina «entity»
    participant Repo as AtribuicaoRepository
    participant Banco as PostgreSQL

    Coordenador ->> Tela: seleciona professor + disciplina + dias letivos
    Tela ->> UseCase: atribuir(professor_id, disciplina_id, dias[])
    UseCase ->> Atrib: calcular_total_minutos(dias, minutos_por_dia_letivo)
    Atrib -->> UseCase: total_minutos
    alt total_minutos >= carga_horaria
        UseCase ->> Repo: salvar(atribuicao, dias)
        Repo ->> Banco: INSERT atribuicao + dias_letivos
        Banco -->> Repo: ok
        Repo -->> UseCase: ok
        UseCase -->> Tela: atribuicao_confirmada
    else total_minutos < carga_horaria
        UseCase -->> Tela: erro_carga_horaria_insuficiente
    end
    Tela -->> Coordenador: exibe resultado
```

Rastreabilidade: mesmos nomes de boundary/control/entity da tabela BCE (`docs/07-boundary-control-entity.md`); mesma ordem de chamada que vira teste de use case no plano de TDD (`docs/11-implementacao-ddd-clean-tdd.md`).

## UC15 — Notificar Atrasos de Entrega (RF12)

```mermaid
sequenceDiagram
    actor Job as JobScheduler «boundary/infra»
    actor Coord as Coordenador
    participant Tela as PainelNotificacoes «boundary»
    participant UC as DetectarAtrasosUseCase «control»
    participant Repo as AtribuicaoRepository
    participant Pref as NotificationPreferenceRepository
    participant Notif as INotifier «port»
    participant SMTP as EmailSmtpNotifier
    participant TG as TelegramNotifier
    participant Log as NotificationLogRepository

    Note over Job,UC: Disparo automático diário (APScheduler)
    Job ->> UC: executar_deteccao_atrasos()
    UC ->> Repo: listar_atribuicoes_pendentes(periodo_ativo)
    Repo -->> UC: atribuicoes_atrasadas[]
    loop para cada atribuicao atrasada
        UC ->> Pref: get_preferencias(usuario_id)
        Pref -->> UC: preferencias {email, telegram, chat_id}
        UC ->> Notif: enviar(destinatario, mensagem)
        alt canal = email
            Notif ->> SMTP: send_msg(smtp_host, smtp_user, ...)
            SMTP -->> Notif: ok / erro
        else canal = telegram
            Notif ->> TG: POST sendMessage(bot_token, chat_id, msg)
            TG -->> Notif: ok / erro
        end
        UC ->> Log: registrar(canal, status, erro?)
        Log -->> UC: persistido
    end
    UC -->> Job: total_enviados / total_falhas

    Note over Coord,UC: Disparo manual via painel
    Coord ->> Tela: clicar "Notificar agora"
    Tela ->> UC: executar_deteccao_atrasos(force=true)
    UC -->> Tela: resumo_envios
    Tela -->> Coord: exibe contadores
```
