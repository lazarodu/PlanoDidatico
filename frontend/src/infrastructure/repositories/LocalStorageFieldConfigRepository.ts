import { IFieldConfigRepository } from '@/domain/repositories/IFieldConfigRepository';
import { FieldConfig } from '@/domain/value-objects/FieldConfig';

const STORAGE_KEY = 'plano_didatico_fields_cache_v1';

const DEFAULT_FIELDS: FieldConfig[] = [
  FieldConfig.create({
    id: 'f-ementa',
    name: 'ementa',
    label: 'Ementa da Disciplina',
    type: 'textarea',
    required: true,
    order: 1,
    defaultValue: 'Conceitos fundamentais, arquitetura e desenvolvimento web moderno.',
  }),
  FieldConfig.create({
    id: 'f-metodologia',
    name: 'metodologia',
    label: 'Metodologia de Ensino',
    type: 'textarea',
    required: true,
    order: 2,
    defaultValue: 'Aulas expositivas e práticas baseadas em projetos com TDD e Clean Architecture.',
  }),
  FieldConfig.create({
    id: 'f-criterios',
    name: 'criterios_avaliacao',
    label: 'Critérios e Instrumentos de Avaliação',
    type: 'textarea',
    required: true,
    order: 3,
    defaultValue: 'Projetos práticos, testes automatizados e entrega contínua.',
  }),
  FieldConfig.create({
    id: 'f-bibliografia',
    name: 'bibliografia',
    label: 'Bibliografia Básica e Complementar',
    type: 'textarea',
    required: false,
    order: 4,
    defaultValue: 'Clean Architecture (Robert C. Martin), Domain-Driven Design (Eric Evans).',
  }),
];

export class LocalStorageFieldConfigRepository implements IFieldConfigRepository {
  private getStorage(): FieldConfig[] {
    if (typeof window === 'undefined') {
      return DEFAULT_FIELDS;
    }
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_FIELDS));
      return DEFAULT_FIELDS;
    }
    try {
      const parsed: any[] = JSON.parse(raw);
      return parsed.map((item) => FieldConfig.create(item));
    } catch {
      return DEFAULT_FIELDS;
    }
  }

  private setStorage(fields: FieldConfig[]): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fields));
  }

  async findAll(): Promise<FieldConfig[]> {
    return this.getStorage().sort((a, b) => a.order - b.order);
  }

  async save(field: FieldConfig): Promise<void> {
    const list = this.getStorage();
    const idx = list.findIndex((f) => f.id === field.id);
    if (idx >= 0) {
      list[idx] = field;
    } else {
      list.push(field);
    }
    this.setStorage(list);
  }

  async delete(id: string): Promise<void> {
    const list = this.getStorage().filter((f) => f.id !== id);
    this.setStorage(list);
  }
}

