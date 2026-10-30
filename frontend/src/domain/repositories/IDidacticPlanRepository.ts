import { DidacticPlan } from '../entities/DidacticPlan';

export interface IDidacticPlanRepository {
  findById(id: string): Promise<DidacticPlan | null>;
  findByProfessorAndPeriodo(professorId: string, periodoLetivoId: string): Promise<DidacticPlan[]>;
  findByPeriodo(periodoLetivoId: string): Promise<DidacticPlan[]>;
  save(plan: DidacticPlan): Promise<void>;
}

