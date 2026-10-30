import { describe, it, expect } from 'vitest';
import { ValidadorCargaHoraria } from '../ValidadorCargaHoraria';

describe('ValidadorCargaHoraria Domain Service (RF11)', () => {
  it('should pass when total de minutos >= carga horária em minutos', () => {
    // Exemplo: 60 horas de carga horária = 3600 minutos
    // 36 dias letivos com 100 minutos cada = 3600 minutos
    const resultado = ValidadorCargaHoraria.validar({
      quantidadeDiasLetivos: 36,
      minutosPorDiaLetivo: 100,
      cargaHorariaHoras: 60,
    });

    expect(resultado.valido).toBe(true);
    expect(resultado.totalMinutosCalculado).toBe(3600);
    expect(resultado.minutosNecessarios).toBe(3600);
    expect(resultado.mensagemErro).toBeUndefined();
  });

  it('should pass when total de minutos exceeds carga horária', () => {
    const resultado = ValidadorCargaHoraria.validar({
      quantidadeDiasLetivos: 40,
      minutosPorDiaLetivo: 100,
      cargaHorariaHoras: 60,
    });

    expect(resultado.valido).toBe(true);
    expect(resultado.totalMinutosCalculado).toBe(4000);
  });

  it('should fail with precise message when total minutos is less by 1 minute', () => {
    // 60 horas = 3600 min. 35 dias * 100 min = 3500 min (falta 100 min)
    const resultado = ValidadorCargaHoraria.validar({
      quantidadeDiasLetivos: 35,
      minutosPorDiaLetivo: 100,
      cargaHorariaHoras: 60,
    });

    expect(resultado.valido).toBe(false);
    expect(resultado.totalMinutosCalculado).toBe(3500);
    expect(resultado.minutosNecessarios).toBe(3600);
    expect(resultado.mensagemErro).toContain('Carga horária insuficiente');
    expect(resultado.mensagemErro).toContain('Faltam 100 minutos');
  });

  it('should reject non-positive values', () => {
    expect(() =>
      ValidadorCargaHoraria.validar({
        quantidadeDiasLetivos: -1,
        minutosPorDiaLetivo: 100,
        cargaHorariaHoras: 60,
      })
    ).toThrow('Quantidade de dias letivos deve ser positiva');
  });
});

