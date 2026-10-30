import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/shared/components/ui/Card';
import { Badge } from '@/shared/components/ui/Badge';
import { Button } from '@/shared/components/ui/Button';
import Link from 'next/link';
import { BookOpen, FileEdit, Clock, CheckCircle, ShieldAlert, Sparkles } from 'lucide-react';
import { PlanStatus } from '@/domain/entities/DidacticPlan';

// Demonstração de Server-Side Rendering (SSR) e metadados com Server Component
export default async function HomePage() {
  const mockPlanos = [
    {
      id: 'plan-pw-2026-1',
      disciplina: 'Laboratório de Programação Web',
      codigo: 'DCC-084',
      professor: 'Prof. Dr. Lazaro',
      periodo: '2026/1',
      status: PlanStatus.RASCUNHO,
      cargaHoraria: '60h',
      ultimaEdicao: 'Hoje às 14:20',
    },
    {
      id: 'plan-es-2026-1',
      disciplina: 'Engenharia de Software',
      codigo: 'DCC-042',
      professor: 'Profª. Maria Silva',
      periodo: '2026/1',
      status: PlanStatus.SUBMETIDO,
      cargaHoraria: '60h',
      ultimaEdicao: 'Ontem',
    },
    {
      id: 'plan-bd-2026-1',
      disciplina: 'Banco de Dados',
      codigo: 'DCC-015',
      professor: 'Prof. João Santos',
      periodo: '2026/1',
      status: PlanStatus.APROVADO,
      cargaHoraria: '90h',
      ultimaEdicao: '28/10/2026',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero / Banner Informativo */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-900 p-8 text-white shadow-xl">
        <div className="relative z-10 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 text-xs font-semibold backdrop-blur-md mb-4 text-blue-100 border border-white/15">
            <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
            Next.js 16 + Clean Architecture + DDD + Offline-First
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl text-white">
            Planos Didáticos Semestrais
          </h1>
          <p className="mt-3 text-sm sm:text-base text-blue-100 leading-relaxed">
            Gestão e acompanhamento institucional dos planos de ensino do CEFET-MG. Edite campos configuráveis em tempo real com garantia de validação e persistência offline.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/planos/plan-pw-2026-1">
              <Button className="bg-white text-blue-700 hover:bg-blue-50 font-semibold shadow-md">
                <FileEdit className="w-4 h-4 mr-1.5" />
                Preencher Plano Didático (Demo)
              </Button>
            </Link>
            <Link href="/atribuicoes">
              <Button variant="outline" className="text-white border-white/30 bg-white/10 hover:bg-white/20">
                Verificador de Carga (RF11)
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Grid de Planos Didáticos */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Planos Didáticos do Período 2026/1</h2>
            <p className="text-xs text-slate-500">Monitoramento de submissão por disciplina e docente</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockPlanos.map((plano) => (
            <Card key={plano.id} className="hover:border-blue-300 transition-all shadow-sm hover:shadow-md flex flex-col justify-between">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {plano.codigo}
                  </span>
                  <Badge status={plano.status} />
                </div>
                <CardTitle className="text-base mt-2 font-bold text-slate-800 line-clamp-1">
                  {plano.disciplina}
                </CardTitle>
                <CardDescription className="text-xs text-slate-500">
                  {plano.professor}
                </CardDescription>
              </CardHeader>

              <CardContent className="py-2 text-xs text-slate-600 space-y-1.5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-1">
                  <span className="text-slate-400">Carga Horária:</span>
                  <span className="font-semibold text-slate-700">{plano.cargaHoraria}</span>
                </div>
                <div className="flex items-center justify-between pt-1">
                  <span className="text-slate-400">Última atualização:</span>
                  <span className="text-slate-700">{plano.ultimaEdicao}</span>
                </div>
              </CardContent>

              <div className="p-4 pt-2 border-t border-slate-100">
                <Link href={`/planos/${plano.id}`} className="w-full">
                  <Button variant="outline" size="sm" className="w-full justify-center">
                    <FileEdit className="w-3.5 h-3.5 mr-1" />
                    Abrir Plano Didático
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
