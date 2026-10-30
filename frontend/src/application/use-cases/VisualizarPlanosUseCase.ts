import { IDidacticPlanRepository } from '../../domain/repositories/IDidacticPlanRepository';
import { DidacticPlan } from '../../domain/entities/DidacticPlan';

export class VisualizarPlanosUseCase {
  constructor(private readonly planRepo: IDidacticPlanRepository) {}

  async porPeriodo(periodoLetivoId: string): Promise<DidacticPlan[]> {
    return this.planRepo.findByPeriodo(periodoLetivoId);
  }

  async porProfessor(professorId: string, periodoLetivoId: string): Promise<DidacticPlan[]> {
    return this.planRepo.findByProfessorAndPeriodo(professorId, periodoLetivoId);
  }

  async obterPorId(id: string): Promise<DidacticPlan | null> {
    return this.planRepo.findById(id);
  }
}

