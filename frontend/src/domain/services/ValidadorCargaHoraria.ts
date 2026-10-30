export interface ValidacaoCargaHorariaInput {
  quantidadeDiasLetivos: number;
  minutosPorDiaLetivo: number;
  cargaHorariaHoras: number;
}

export interface ValidacaoCargaHorariaResultado {
  valido: boolean;
  totalMinutosCalculado: number;
  minutosNecessarios: number;
  mensagemErro?: string;
}

export class ValidadorCargaHoraria {
  public static validar(input: ValidacaoCargaHorariaInput): ValidacaoCargaHorariaResultado {
    const { quantidadeDiasLetivos, minutosPorDiaLetivo, cargaHorariaHoras } = input;

    if (quantidadeDiasLetivos < 0) {
      throw new Error('Quantidade de dias letivos deve ser positiva');
    }
    if (minutosPorDiaLetivo <= 0) {
      throw new Error('Minutos por dia letivo deve ser maior que zero');
    }
    if (cargaHorariaHoras <= 0) {
      throw new Error('Carga horária deve ser maior que zero');
    }

    const totalMinutosCalculado = quantidadeDiasLetivos * minutosPorDiaLetivo;
    const minutosNecessarios = cargaHorariaHoras * 60;

    const valido = totalMinutosCalculado >= minutosNecessarios;

    if (!valido) {
      const diferenca = minutosNecessarios - totalMinutosCalculado;
      return {
        valido: false,
        totalMinutosCalculado,
        minutosNecessarios,
        mensagemErro: `Carga horária insuficiente: planejado ${totalMinutosCalculado} min (${(totalMinutosCalculado / 60).toFixed(1)}h), necessário ${minutosNecessarios} min (${cargaHorariaHoras}h). Faltam ${diferenca} minutos.`,
      };
    }

    return {
      valido: true,
      totalMinutosCalculado,
      minutosNecessarios,
    };
  }
}

