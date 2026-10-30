import { IDidacticPlanRepository } from '@/domain/repositories/IDidacticPlanRepository';
import { DidacticPlan, PlanStatus } from '@/domain/entities/DidacticPlan';

const STORAGE_KEY = 'plano_didatico_plans_cache_v1';

export class LocalStorageDidacticPlanRepository implements IDidacticPlanRepository {
  private getStorage(): Record<string, any> {
    if (typeof window === 'undefined') {
      return {};
    }
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return {};
    try {
      return JSON.parse(data);
    } catch {
      return {};
    }
  }

  private setStorage(data: Record<string, any>): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  async findById(id: string): Promise<DidacticPlan | null> {
    // Primeiro tenta da API se online, se offline cai no cache local
    const storage = this.getStorage();
    const raw = storage[id];
    if (!raw) return null;
    return DidacticPlan.create(raw);
  }

  async findByProfessorAndPeriodo(professorId: string, periodoLetivoId: string): Promise<DidacticPlan[]> {
    const storage = this.getStorage();
    const plans: DidacticPlan[] = [];
    for (const key of Object.keys(storage)) {
      const raw = storage[key];
      if (raw.professorId === professorId && raw.periodoLetivoId === periodoLetivoId) {
        plans.push(DidacticPlan.create(raw));
      }
    }
    return plans;
  }

  async findByPeriodo(periodoLetivoId: string): Promise<DidacticPlan[]> {
    const storage = this.getStorage();
    const plans: DidacticPlan[] = [];
    for (const key of Object.keys(storage)) {
      const raw = storage[key];
      if (raw.periodoLetivoId === periodoLetivoId) {
        plans.push(DidacticPlan.create(raw));
      }
    }
    return plans;
  }

  async save(plan: DidacticPlan): Promise<void> {
    const storage = this.getStorage();
    storage[plan.id] = plan.toJSON();
    this.setStorage(storage);
  }
}

