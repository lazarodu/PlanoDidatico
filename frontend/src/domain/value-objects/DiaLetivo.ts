export type Turno = 'matutino' | 'vespertino' | 'noturno' | 'integral';

export class DiaLetivo {
  readonly data: string; // YYYY-MM-DD
  readonly turno: Turno;

  private constructor(data: string, turno: Turno) {
    this.data = data;
    this.turno = turno;
  }

  public static create(data: string, turno: Turno): DiaLetivo {
    const isoDateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!isoDateRegex.test(data) || isNaN(new Date(data).getTime())) {
      throw new Error('Data inválida. Use o formato YYYY-MM-DD');
    }
    const turnosValidos: Turno[] = ['matutino', 'vespertino', 'noturno', 'integral'];
    if (!turnosValidos.includes(turno)) {
      throw new Error(`Turno inválido: ${turno}`);
    }
    return new DiaLetivo(data, turno);
  }

  public equals(other: DiaLetivo): boolean {
    if (!other) return false;
    return this.data === other.data && this.turno === other.turno;
  }
}

