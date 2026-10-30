import { FieldConfig } from '../value-objects/FieldConfig';

export interface IFieldConfigRepository {
  findAll(): Promise<FieldConfig[]>;
  save(field: FieldConfig): Promise<void>;
  delete(id: string): Promise<void>;
}

