import { DidacticPlan } from '../../domain/entities/DidacticPlan';
import { IDidacticPlanRepository } from '../../domain/repositories/IDidacticPlanRepository';
import { IFieldConfigRepository } from '../../domain/repositories/IFieldConfigRepository';

export interface SubmeterPlanoInput {
  planId: string;
  disciplinaId: string;
  disciplinaNome: string;
  professorId: string;
  professorNome: string;
  periodoLetivoId: string;
  camposValores: Record<string, any>;
  isSubmissaoFinal: boolean;
}

export interface SubmeterPlanoOutput {
  success: boolean;
  plan?: DidacticPlan;
  erros?: Record<string, string>;
  mensagem?: string;
}

export class SubmeterPlanoUseCase {
  constructor(
    private readonly planRepo: IDidacticPlanRepository,
    private readonly fieldRepo: IFieldConfigRepository
  ) {}

  async execute(input: SubmeterPlanoInput): Promise<SubmeterPlanoOutput> {
    const fields = await this.fieldRepo.findAll();

    let plan = await this.planRepo.findById(input.planId);

    if (!plan) {
      plan = DidacticPlan.create({
        id: input.planId,
        disciplinaId: input.disciplinaId,
        disciplinaNome: input.disciplinaNome,
        professorId: input.professorId,
        professorNome: input.professorNome,
        periodoLetivoId: input.periodoLetivoId,
        camposValores: input.camposValores,
      });
    } else {
      for (const [campo, valor] of Object.entries(input.camposValores)) {
        plan.updateCampo(campo, valor);
      }
    }

    if (input.isSubmissaoFinal) {
      const validation = plan.validateSubmission(fields);
      if (!validation.valido) {
        return {
          success: false,
          erros: validation.erros,
          mensagem: 'Campos obrigatórios estão pendentes.',
        };
      }
      plan.submeter(fields);
    }

    await this.planRepo.save(plan);

    return {
      success: true,
      plan,
      mensagem: input.isSubmissaoFinal ? 'Plano didático submetido com sucesso!' : 'Rascunho salvo com sucesso.',
    };
  }
}

