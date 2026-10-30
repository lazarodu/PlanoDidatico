import { describe, it, expect } from 'vitest';
import { DiaLetivo } from '../DiaLetivo';

describe('DiaLetivo Value Object', () => {
  it('should create an immutable DiaLetivo with date and turno', () => {
    const dia = DiaLetivo.create('2026-03-02', 'noturno');
    expect(dia.data).toBe('2026-03-02');
    expect(dia.turno).toBe('noturno');
  });

  it('should throw error on invalid date format', () => {
    expect(() => DiaLetivo.create('02/03/2026', 'noturno')).toThrow('Data inválida');
  });

  it('should compare equality by value', () => {
    const dia1 = DiaLetivo.create('2026-03-02', 'matutino');
    const dia2 = DiaLetivo.create('2026-03-02', 'matutino');
    const dia3 = DiaLetivo.create('2026-03-02', 'vespertino');

    expect(dia1.equals(dia2)).toBe(true);
    expect(dia1.equals(dia3)).toBe(false);
  });
});

