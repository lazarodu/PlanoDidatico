import { describe, it, expect } from 'vitest';
import { DidacticPlan, PlanStatus } from '../DidacticPlan';
import { FieldConfig } from '../../value-objects/FieldConfig';

describe('DidacticPlan Aggregate Root (RF01, RF05)', () => {
  const fields = [
    FieldConfig.create({ id: '1', name: 'metodologia', label: 'Metodologia', type: 'textarea', required: true }),
    FieldConfig.create({ id: '2', name: 'criterios_avaliacao', label: 'Critérios de Avaliação', type: 'textarea', required: true }),
  ];

  it('should create a new plan in DRAFT status', () => {
    const plan = DidacticPlan.create({
      id: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório de Programação Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: 'periodo-2026-1',
      camposValores: {
        metodologia: 'Aulas práticas em laboratório',
      },
    });

    expect(plan.id).toBe('plan-1');
    expect(plan.status).toBe(PlanStatus.RASCUNHO);
    expect(plan.camposValores['metodologia']).toBe('Aulas práticas em laboratório');
  });

  it('should update field value when plan is editable', () => {
    const plan = DidacticPlan.create({
      id: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório de Programação Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: 'periodo-2026-1',
      camposValores: {},
    });

    plan.updateCampo('metodologia', 'Nova metodologia ativa');
    expect(plan.camposValores['metodologia']).toBe('Nova metodologia ativa');
  });

  it('should fail submission if required fields are missing', () => {
    const plan = DidacticPlan.create({
      id: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório de Programação Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: 'periodo-2026-1',
      camposValores: {
        metodologia: 'Alguma metodologia',
        // criterios_avaliacao is missing
      },
    });

    const resultado = plan.validateSubmission(fields);
    expect(resultado.valido).toBe(false);
    expect(resultado.erros['criterios_avaliacao']).toBe('O campo Critérios de Avaliação é obrigatório');
    expect(() => plan.submeter(fields)).toThrow('Não é possível submeter o plano didático com campos obrigatórios pendentes');
  });

  it('should submit successfully when all required fields are present', () => {
    const plan = DidacticPlan.create({
      id: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório de Programação Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: 'periodo-2026-1',
      camposValores: {
        metodologia: 'Metodologia ativa e TDD',
        criterios_avaliacao: 'Provas e projetos práticos',
      },
    });

    plan.submeter(fields);
    expect(plan.status).toBe(PlanStatus.SUBMETIDO);
    expect(plan.dataSubmissao).toBeDefined();
  });

  it('should not allow modification once approved', () => {
    const plan = DidacticPlan.create({
      id: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório de Programação Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: 'periodo-2026-1',
      camposValores: {
        metodologia: 'Metodologia ativa',
        criterios_avaliacao: 'Provas',
      },
    });

    plan.submeter(fields);
    plan.aprovar();
    expect(plan.status).toBe(PlanStatus.APROVADO);
    expect(() => plan.updateCampo('metodologia', 'tentativa')).toThrow('Plano não pode ser alterado após aprovação');
  });
});

