import { AtribuicaoProfessorDisciplina } from '../entities/AtribuicaoProfessorDisciplina';

export interface IAtribuicaoRepository {
  findById(id: string): Promise<AtribuicaoProfessorDisciplina | null>;
  findByPeriodo(periodoLetivoId: string): Promise<AtribuicaoProfessorDisciplina[]>;
  findByProfessor(professorId: string, periodoLetivoId: string): Promise<AtribuicaoProfessorDisciplina[]>;
  save(atribuicao: AtribuicaoProfessorDisciplina): Promise<void>;
}

