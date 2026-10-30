import { describe, it, expect } from 'vitest';
import { FieldConfig } from '../FieldConfig';

describe('FieldConfig Value Object', () => {
  it('should create a valid text field config', () => {
    const field = FieldConfig.create({
      id: 'field-1',
      name: 'metodologia',
      label: 'Metodologia de Ensino',
      type: 'textarea',
      required: true,
      order: 1,
    });

    expect(field.id).toBe('field-1');
    expect(field.name).toBe('metodologia');
    expect(field.label).toBe('Metodologia de Ensino');
    expect(field.type).toBe('textarea');
    expect(field.required).toBe(true);
  });

  it('should throw error if name is empty', () => {
    expect(() =>
      FieldConfig.create({
        id: 'field-2',
        name: '',
        label: 'Título',
        type: 'text',
        required: true,
      })
    ).toThrow('O nome do campo não pode ser vazio');
  });

  it('should validate value according to field rules', () => {
    const field = FieldConfig.create({
      id: 'field-3',
      name: 'ementa',
      label: 'Ementa',
      type: 'text',
      required: true,
    });

    expect(field.validate('')).toBe('O campo Ementa é obrigatório');
    expect(field.validate('Conteúdo de teste')).toBeNull();
  });
});
