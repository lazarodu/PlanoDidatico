import { describe, it, expect, beforeEach } from 'vitest';
import { SubmeterPlanoUseCase } from '../SubmeterPlanoUseCase';
import { DidacticPlan, PlanStatus } from '../../../domain/entities/DidacticPlan';
import { FieldConfig } from '../../../domain/value-objects/FieldConfig';
import { IDidacticPlanRepository } from '../../../domain/repositories/IDidacticPlanRepository';
import { IFieldConfigRepository } from '../../../domain/repositories/IFieldConfigRepository';

class InMemoryDidacticPlanRepository implements IDidacticPlanRepository {
  public plans: Map<string, DidacticPlan> = new Map();

  async findById(id: string): Promise<DidacticPlan | null> {
    return this.plans.get(id) || null;
  }

  async findByProfessorAndPeriodo(professorId: string, periodoLetivoId: string): Promise<DidacticPlan[]> {
    return Array.from(this.plans.values()).filter(
      (p) => p.professorId === professorId && p.periodoLetivoId === periodoLetivoId
    );
  }

  async findByPeriodo(periodoLetivoId: string): Promise<DidacticPlan[]> {
    return Array.from(this.plans.values()).filter((p) => p.periodoLetivoId === periodoLetivoId);
  }

  async save(plan: DidacticPlan): Promise<void> {
    this.plans.set(plan.id, plan);
  }
}

class InMemoryFieldConfigRepository implements IFieldConfigRepository {
  public fields: FieldConfig[] = [];

  async findAll(): Promise<FieldConfig[]> {
    return [...this.fields];
  }

  async save(field: FieldConfig): Promise<void> {
    const idx = this.fields.findIndex((f) => f.id === field.id);
    if (idx >= 0) this.fields[idx] = field;
    else this.fields.push(field);
  }

  async delete(id: string): Promise<void> {
    this.fields = this.fields.filter((f) => f.id !== id);
  }
}

describe('SubmeterPlanoUseCase (UC1 - Clean Architecture)', () => {
  let planRepo: InMemoryDidacticPlanRepository;
  let fieldRepo: InMemoryFieldConfigRepository;
  let useCase: SubmeterPlanoUseCase;

  beforeEach(() => {
    planRepo = new InMemoryDidacticPlanRepository();
    fieldRepo = new InMemoryFieldConfigRepository();
    useCase = new SubmeterPlanoUseCase(planRepo, fieldRepo);

    fieldRepo.fields = [
      FieldConfig.create({ id: 'f1', name: 'metodologia', label: 'Metodologia', type: 'textarea', required: true }),
      FieldConfig.create({ id: 'f2', name: 'criterios', label: 'Critérios', type: 'textarea', required: true }),
    ];
  });

  it('should save draft when submit is false', async () => {
    const result = await useCase.execute({
      planId: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: '2026-1',
      camposValores: { metodologia: 'Metodologia Rascunho' },
      isSubmissaoFinal: false,
    });

    expect(result.success).toBe(true);
    expect(result.plan?.status).toBe(PlanStatus.RASCUNHO);

    const saved = await planRepo.findById('plan-1');
    expect(saved?.camposValores['metodologia']).toBe('Metodologia Rascunho');
  });

  it('should reject final submission if required fields are missing', async () => {
    const result = await useCase.execute({
      planId: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: '2026-1',
      camposValores: { metodologia: 'Apenas metodologia' },
      isSubmissaoFinal: true,
    });

    expect(result.success).toBe(false);
    expect(result.erros?.['criterios']).toBe('O campo Critérios é obrigatório');
  });

  it('should submit plan successfully when all fields are valid', async () => {
    const result = await useCase.execute({
      planId: 'plan-1',
      disciplinaId: 'disc-1',
      disciplinaNome: 'Laboratório Web',
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
      periodoLetivoId: '2026-1',
      camposValores: {
        metodologia: 'Metodologia completa',
        criterios: 'Avaliação contínua',
      },
      isSubmissaoFinal: true,
    });

    expect(result.success).toBe(true);
    expect(result.plan?.status).toBe(PlanStatus.SUBMETIDO);
    expect(result.plan?.dataSubmissao).toBeDefined();
  });
});

