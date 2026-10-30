'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/shared/components/ui/Card';
import { Button } from '@/shared/components/ui/Button';
import { Input } from '@/shared/components/ui/Input';
import { ValidadorCargaHoraria, ValidacaoCargaHorariaResultado } from '@/domain/services/ValidadorCargaHoraria';
import { DiaLetivo, Turno } from '@/domain/value-objects/DiaLetivo';
import { AtribuicaoProfessorDisciplina } from '@/domain/entities/AtribuicaoProfessorDisciplina';
import { Calendar, CheckCircle2, AlertCircle, Plus, Trash2, Clock, Calculator } from 'lucide-react';

export default function AtribuicoesPage() {
  const [cargaHorariaHoras, setCargaHorariaHoras] = useState<number>(60);
  const [minutosPorDiaLetivo, setMinutosPorDiaLetivo] = useState<number>(100);
  const [dataInput, setDataInput] = useState<string>('2026-03-02');
  const [turnoInput, setTurnoInput] = useState<Turno>('noturno');
  const [dias, setDias] = useState<DiaLetivo[]>([
    DiaLetivo.create('2026-03-02', 'noturno'),
    DiaLetivo.create('2026-03-09', 'noturno'),
    DiaLetivo.create('2026-03-16', 'noturno'),
    DiaLetivo.create('2026-03-23', 'noturno'),
  ]);
  const [erroAdd, setErroAdd] = useState<string | null>(null);

  // Instancia Aggregate Root e executa Domain Service de validação (RF11)
  const atribuicao = AtribuicaoProfessorDisciplina.create({
    id: 'atrib-demo-1',
    periodoLetivoId: '2026/1',
    disciplinaId: 'dcc-084',
    disciplinaNome: 'Laboratório de Programação Web',
    cargaHorariaHoras,
    minutosPorDiaLetivo,
    professorId: 'prof-1',
    professorNome: 'Prof. Dr. Lazaro',
    diasLetivos: dias,
  });

  const validacao: ValidacaoCargaHorariaResultado = atribuicao.validarCargaHoraria();

  const handleAddDia = (e: React.FormEvent) => {
    e.preventDefault();
    setErroAdd(null);
    try {
      const novoDia = DiaLetivo.create(dataInput, turnoInput);
      if (dias.some((d) => d.equals(novoDia))) {
        setErroAdd('Este dia e turno já constam na grade.');
        return;
      }
      setDias((prev) => [...prev, novoDia]);
    } catch (err: any) {
      setErroAdd(err.message || 'Erro ao adicionar dia letivo.');
    }
  };

  const handleRemoveDia = (index: number) => {
    setDias((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Calendar className="w-6 h-6 text-blue-600" />
          Atribuição de Disciplinas e Validador de Carga Horária (RF11)
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Regra de Domínio: <code>(dias letivos × minutos_por_dia_letivo) ≥ carga_horaria</code> em minutos.
        </p>
      </div>

      {/* Card com o Status da Validação de Domínio (RF11) */}
      <div
        className={`p-5 rounded-xl border flex items-start gap-4 transition-all shadow-sm ${
          validacao.valido
            ? 'bg-emerald-50 border-emerald-300 text-emerald-900'
            : 'bg-amber-50 border-amber-300 text-amber-900'
        }`}
      >
        {validacao.valido ? (
          <CheckCircle2 className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-0.5" />
        ) : (
          <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
        )}
        <div className="space-y-1 flex-1">
          <h4 className="font-bold text-base">
            {validacao.valido ? 'Carga Horária Válida e Cumprida' : 'Carga Horária Pendente / Insuficiente'}
          </h4>
          <p className="text-sm">
            {validacao.valido
              ? `O total planejado de ${validacao.totalMinutosCalculado} minutos (${(validacao.totalMinutosCalculado / 60).toFixed(1)}h) atende ou supera a exigência de ${validacao.minutosNecessarios} minutos (${cargaHorariaHoras}h).`
              : validacao.mensagemErro}
          </p>
          <div className="flex items-center gap-4 text-xs font-semibold pt-1">
            <span>Dias alocados: {dias.length}</span>
            <span>Total minutos: {validacao.totalMinutosCalculado} min</span>
            <span>Meta: {validacao.minutosNecessarios} min</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Painel de Configurações da Disciplina */}
        <Card className="lg:col-span-1 shadow-sm">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Calculator className="w-4 h-4 text-blue-600" />
              Parâmetros da Disciplina
            </CardTitle>
            <CardDescription className="text-xs">Valores definidos no Período Letivo</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="number"
              label="Carga Horária (Horas)"
              value={cargaHorariaHoras}
              onChange={(e) => setCargaHorariaHoras(Number(e.target.value))}
              min={1}
            />
            <Input
              type="number"
              label="Minutos por Dia Letivo"
              value={minutosPorDiaLetivo}
              onChange={(e) => setMinutosPorDiaLetivo(Number(e.target.value))}
              min={1}
            />

            <div className="p-3 bg-slate-50 rounded-lg text-xs space-y-1 text-slate-600 border border-slate-200">
              <p><strong>Cálculo:</strong></p>
              <p>{dias.length} dias × {minutosPorDiaLetivo} min = {dias.length * minutosPorDiaLetivo} min</p>
              <p>Meta ({cargaHorariaHoras}h × 60min) = {cargaHorariaHoras * 60} min</p>
            </div>
          </CardContent>
        </Card>

        {/* Adicionar e Listar Dias Letivos */}
        <Card className="lg:col-span-2 shadow-sm">
          <CardHeader>
            <CardTitle className="text-base">Grade de Dias Letivos (Aggregate Root)</CardTitle>
            <CardDescription className="text-xs">
              Adicione os dias do calendário letivo atribuídos à disciplina
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <form onSubmit={handleAddDia} className="flex flex-col sm:flex-row gap-3 items-end">
              <div className="flex-1 w-full">
                <Input
                  type="date"
                  label="Data do Dia Letivo"
                  value={dataInput}
                  onChange={(e) => setDataInput(e.target.value)}
                  required
                />
              </div>
              <div className="w-full sm:w-44">
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Turno</label>
                <select
                  className="w-full h-10 px-3 py-2 rounded-md border border-slate-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={turnoInput}
                  onChange={(e) => setTurnoInput(e.target.value as Turno)}
                >
                  <option value="matutino">Matutino</option>
                  <option value="vespertino">Vespertino</option>
                  <option value="noturno">Noturno</option>
                  <option value="integral">Integral</option>
                </select>
              </div>
              <Button type="submit" variant="primary" className="w-full sm:w-auto h-10">
                <Plus className="w-4 h-4 mr-1" />
                Adicionar
              </Button>
            </form>

            {erroAdd && <p className="text-xs font-semibold text-rose-600">{erroAdd}</p>}

            <div className="space-y-2">
              <h5 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Dias Cadastrados ({dias.length})
              </h5>
              <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 border border-slate-200 rounded-lg">
                {dias.length === 0 ? (
                  <p className="p-4 text-center text-xs text-slate-400">Nenhum dia letivo alocado.</p>
                ) : (
                  dias.map((d, index) => (
                    <div key={index} className="flex items-center justify-between p-3 hover:bg-slate-50 transition-colors">
                      <div className="flex items-center gap-3">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        <div>
                          <p className="text-sm font-medium text-slate-800">{d.data}</p>
                          <span className="text-xs text-slate-400 capitalize">Turno: {d.turno}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveDia(index)}
                        className="text-slate-400 hover:text-rose-600 p-1 rounded transition-colors"
                        title="Remover dia"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

