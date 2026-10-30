import { IFieldConfigRepository } from '../../domain/repositories/IFieldConfigRepository';
import { FieldConfig } from '../../domain/value-objects/FieldConfig';

export class GerenciarCamposUseCase {
  constructor(private readonly fieldRepo: IFieldConfigRepository) {}

  async listar(): Promise<FieldConfig[]> {
    return this.fieldRepo.findAll();
  }

  async salvar(field: FieldConfig): Promise<void> {
    await this.fieldRepo.save(field);
  }

  async remover(id: string): Promise<void> {
    await this.fieldRepo.delete(id);
  }
}

