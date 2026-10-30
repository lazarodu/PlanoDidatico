import { DiaLetivo } from '../value-objects/DiaLetivo';
import { ValidadorCargaHoraria, ValidacaoCargaHorariaResultado } from '../services/ValidadorCargaHoraria';

export interface AtribuicaoProps {
  id: string;
  periodoLetivoId: string;
  disciplinaId: string;
  disciplinaNome: string;
  cargaHorariaHoras: number;
  minutosPorDiaLetivo: number;
  professorId: string;
  professorNome: string;
  diasLetivos?: DiaLetivo[];
}

export class AtribuicaoProfessorDisciplina {
  readonly id: string;
  readonly periodoLetivoId: string;
  readonly disciplinaId: string;
  readonly disciplinaNome: string;
  readonly cargaHorariaHoras: number;
  readonly minutosPorDiaLetivo: number;
  readonly professorId: string;
  readonly professorNome: string;
  private _diasLetivos: DiaLetivo[];

  private constructor(props: AtribuicaoProps) {
    this.id = props.id;
    this.periodoLetivoId = props.periodoLetivoId;
    this.disciplinaId = props.disciplinaId;
    this.disciplinaNome = props.disciplinaNome;
    this.cargaHorariaHoras = props.cargaHorariaHoras;
    this.minutosPorDiaLetivo = props.minutosPorDiaLetivo;
    this.professorId = props.professorId;
    this.professorNome = props.professorNome;
    this._diasLetivos = props.diasLetivos ? [...props.diasLetivos] : [];
  }

  public static create(props: AtribuicaoProps): AtribuicaoProfessorDisciplina {
    if (!props.id) throw new Error('ID é obrigatório');
    if (!props.disciplinaId) throw new Error('Disciplina é obrigatória');
    if (!props.professorId) throw new Error('Professor é obrigatório');
    if (!props.periodoLetivoId) throw new Error('Período letivo é obrigatório');
    if (props.cargaHorariaHoras <= 0) throw new Error('Carga horária deve ser positiva');
    if (props.minutosPorDiaLetivo <= 0) throw new Error('Minutos por dia letivo deve ser positivo');

    return new AtribuicaoProfessorDisciplina(props);
  }

  get diasLetivos(): readonly DiaLetivo[] {
    return this._diasLetivos;
  }

  get totalMinutosAlocados(): number {
    return this._diasLetivos.length * this.minutosPorDiaLetivo;
  }

  public adicionarDiaLetivo(dia: DiaLetivo): void {
    const jaExiste = this._diasLetivos.some((d) => d.equals(dia));
    if (jaExiste) {
      throw new Error('Dia letivo já atribuído a esta disciplina');
    }
    this._diasLetivos.push(dia);
  }

  public removerDiaLetivo(dia: DiaLetivo): void {
    this._diasLetivos = this._diasLetivos.filter((d) => !d.equals(dia));
  }

  public validarCargaHoraria(): ValidacaoCargaHorariaResultado {
    return ValidadorCargaHoraria.validar({
      quantidadeDiasLetivos: this._diasLetivos.length,
      minutosPorDiaLetivo: this.minutosPorDiaLetivo,
      cargaHorariaHoras: this.cargaHorariaHoras,
    });
  }
}

