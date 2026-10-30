import { FieldConfig } from '../value-objects/FieldConfig';

export enum PlanStatus {
  RASCUNHO = 'RASCUNHO',
  SUBMETIDO = 'SUBMETIDO',
  APROVADO = 'APROVADO',
  REJEITADO = 'REJEITADO',
}

export interface DidacticPlanProps {
  id: string;
  disciplinaId: string;
  disciplinaNome: string;
  professorId: string;
  professorNome: string;
  periodoLetivoId: string;
  status?: PlanStatus;
  camposValores?: Record<string, any>;
  dataCriacao?: string;
  dataSubmissao?: string;
  observacoesCoordenador?: string;
}

export interface SubmissionValidationResult {
  valido: boolean;
  erros: Record<string, string>;
}

export class DidacticPlan {
  readonly id: string;
  readonly disciplinaId: string;
  readonly disciplinaNome: string;
  readonly professorId: string;
  readonly professorNome: string;
  readonly periodoLetivoId: string;
  private _status: PlanStatus;
  private _camposValores: Record<string, any>;
  readonly dataCriacao: string;
  private _dataSubmissao?: string;
  private _observacoesCoordenador?: string;

  private constructor(props: DidacticPlanProps) {
    this.id = props.id;
    this.disciplinaId = props.disciplinaId;
    this.disciplinaNome = props.disciplinaNome;
    this.professorId = props.professorId;
    this.professorNome = props.professorNome;
    this.periodoLetivoId = props.periodoLetivoId;
    this._status = props.status ?? PlanStatus.RASCUNHO;
    this._camposValores = props.camposValores ? { ...props.camposValores } : {};
    this.dataCriacao = props.dataCriacao ?? new Date().toISOString();
    this._dataSubmissao = props.dataSubmissao;
    this._observacoesCoordenador = props.observacoesCoordenador;
  }

  public static create(props: DidacticPlanProps): DidacticPlan {
    if (!props.id) throw new Error('ID do plano é obrigatório');
    if (!props.disciplinaId) throw new Error('Disciplina é obrigatória');
    if (!props.professorId) throw new Error('Professor é obrigatório');
    if (!props.periodoLetivoId) throw new Error('Período letivo é obrigatório');

    return new DidacticPlan(props);
  }

  get status(): PlanStatus {
    return this._status;
  }

  get camposValores(): Record<string, any> {
    return { ...this._camposValores };
  }

  get dataSubmissao(): string | undefined {
    return this._dataSubmissao;
  }

  get observacoesCoordenador(): string | undefined {
    return this._observacoesCoordenador;
  }

  public updateCampo(campoNome: string, valor: any): void {
    if (this._status === PlanStatus.APROVADO) {
      throw new Error('Plano não pode ser alterado após aprovação');
    }
    this._camposValores[campoNome] = valor;
  }

  public validateSubmission(fields: FieldConfig[]): SubmissionValidationResult {
    const erros: Record<string, string> = {};

    for (const field of fields) {
      const valor = this._camposValores[field.name];
      const erro = field.validate(valor);
      if (erro) {
        erros[field.name] = erro;
      }
    }

    return {
      valido: Object.keys(erros).length === 0,
      erros,
    };
  }

  public submeter(fields: FieldConfig[]): void {
    const validation = this.validateSubmission(fields);
    if (!validation.valido) {
      throw new Error('Não é possível submeter o plano didático com campos obrigatórios pendentes');
    }
    this._status = PlanStatus.SUBMETIDO;
    this._dataSubmissao = new Date().toISOString();
  }

  public aprovar(): void {
    if (this._status !== PlanStatus.SUBMETIDO) {
      throw new Error('Apenas planos submetidos podem ser aprovados');
    }
    this._status = PlanStatus.APROVADO;
  }

  public rejeitar(motivo: string): void {
    if (this._status !== PlanStatus.SUBMETIDO) {
      throw new Error('Apenas planos submetidos podem ser rejeitados');
    }
    this._status = PlanStatus.REJEITADO;
    this._observacoesCoordenador = motivo;
  }

  public toJSON(): DidacticPlanProps {
    return {
      id: this.id,
      disciplinaId: this.disciplinaId,
      disciplinaNome: this.disciplinaNome,
      professorId: this.professorId,
      professorNome: this.professorNome,
      periodoLetivoId: this.periodoLetivoId,
      status: this._status,
      camposValores: this.camposValores,
      dataCriacao: this.dataCriacao,
      dataSubmissao: this._dataSubmissao,
      observacoesCoordenador: this._observacoesCoordenador,
    };
  }
}

