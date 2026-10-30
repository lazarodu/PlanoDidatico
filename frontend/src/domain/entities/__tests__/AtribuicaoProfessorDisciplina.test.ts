import { describe, it, expect } from 'vitest';
import { AtribuicaoProfessorDisciplina } from '../AtribuicaoProfessorDisciplina';
import { DiaLetivo } from '../../value-objects/DiaLetivo';

describe('AtribuicaoProfessorDisciplina Aggregate Root (RF10, RF11)', () => {
  it('should initialize with empty dias letivos and calculate minutes', () => {
    const atribuicao = AtribuicaoProfessorDisciplina.create({
      id: 'atrib-1',
      periodoLetivoId: 'periodo-2026-1',
      disciplinaId: 'disc-web',
      disciplinaNome: 'Laboratório de Programação Web',
      cargaHorariaHoras: 60,
      minutosPorDiaLetivo: 100,
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
    });

    expect(atribuicao.diasLetivos.length).toBe(0);
    expect(atribuicao.totalMinutosAlocados).toBe(0);
  });

  it('should add unique dias letivos through aggregate root', () => {
    const atribuicao = AtribuicaoProfessorDisciplina.create({
      id: 'atrib-1',
      periodoLetivoId: 'periodo-2026-1',
      disciplinaId: 'disc-web',
      disciplinaNome: 'Laboratório de Programação Web',
      cargaHorariaHoras: 60,
      minutosPorDiaLetivo: 100,
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
    });

    const dia1 = DiaLetivo.create('2026-03-02', 'noturno');
    const dia2 = DiaLetivo.create('2026-03-09', 'noturno');

    atribuicao.adicionarDiaLetivo(dia1);
    atribuicao.adicionarDiaLetivo(dia2);

    expect(atribuicao.diasLetivos.length).toBe(2);
    expect(atribuicao.totalMinutosAlocados).toBe(200);

    // Duplicated date + shift should throw
    expect(() => atribuicao.adicionarDiaLetivo(dia1)).toThrow('Dia letivo já atribuído a esta disciplina');
  });

  it('should validate total carga horaria via domain service validation', () => {
    const atribuicao = AtribuicaoProfessorDisciplina.create({
      id: 'atrib-1',
      periodoLetivoId: 'periodo-2026-1',
      disciplinaId: 'disc-web',
      disciplinaNome: 'Laboratório de Programação Web',
      cargaHorariaHoras: 2, // 120 minutos
      minutosPorDiaLetivo: 60,
      professorId: 'prof-1',
      professorNome: 'Prof. Carlos',
    });

    // 1 dia = 60 min < 120 min
    atribuicao.adicionarDiaLetivo(DiaLetivo.create('2026-03-02', 'noturno'));
    let validacao = atribuicao.validarCargaHoraria();
    expect(validacao.valido).toBe(false);

    // 2 dias = 120 min >= 120 min
    atribuicao.adicionarDiaLetivo(DiaLetivo.create('2026-03-09', 'noturno'));
    validacao = atribuicao.validarCargaHoraria();
    expect(validacao.valido).toBe(true);
  });
});

