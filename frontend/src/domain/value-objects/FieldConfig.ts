export type FieldType = 'text' | 'textarea' | 'number' | 'select' | 'date';

export interface FieldConfigProps {
  id: string;
  name: string;
  label: string;
  type: FieldType;
  required?: boolean;
  options?: string[];
  order?: number;
  defaultValue?: string | number;
}

export class FieldConfig {
  readonly id: string;
  readonly name: string;
  readonly label: string;
  readonly type: FieldType;
  readonly required: boolean;
  readonly options?: string[];
  readonly order: number;
  readonly defaultValue?: string | number;

  private constructor(props: FieldConfigProps) {
    this.id = props.id;
    this.name = props.name;
    this.label = props.label;
    this.type = props.type;
    this.required = props.required ?? false;
    this.options = props.options;
    this.order = props.order ?? 0;
    this.defaultValue = props.defaultValue;
  }

  public static create(props: FieldConfigProps): FieldConfig {
    if (!props.id || props.id.trim() === '') {
      throw new Error('O ID do campo não pode ser vazio');
    }
    if (!props.name || props.name.trim() === '') {
      throw new Error('O nome do campo não pode ser vazio');
    }
    if (!props.label || props.label.trim() === '') {
      throw new Error('O rótulo do campo não pode ser vazio');
    }
    return new FieldConfig(props);
  }

  public validate(value: unknown): string | null {
    if (this.required) {
      if (value === undefined || value === null || (typeof value === 'string' && value.trim() === '')) {
        return `O campo ${this.label} é obrigatório`;
      }
    }
    return null;
  }
}

