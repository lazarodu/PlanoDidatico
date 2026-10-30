'use client';

import React, { use, useEffect, useState } from 'react';
import { PlanForm } from '@/presentation/components/PlanForm';
import { LocalStorageFieldConfigRepository } from '@/infrastructure/repositories/LocalStorageFieldConfigRepository';
import { LocalStorageDidacticPlanRepository } from '@/infrastructure/repositories/LocalStorageDidacticPlanRepository';
import { SubmeterPlanoUseCase } from '@/application/use-cases/SubmeterPlanoUseCase';
import { FieldConfig } from '@/domain/value-objects/FieldConfig';
import { DidacticPlan, PlanStatus } from '@/domain/entities/DidacticPlan';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import Link from 'next/link';

interface PlanPageProps {
  params: Promise<{ id: string }>;
}

export default function PlanEditorPage({ params }: PlanPageProps) {
  const resolvedParams = use(params);
  const planId = resolvedParams.id;

  const queryClient = useQueryClient();
  const fieldRepo = React.useMemo(() => new LocalStorageFieldConfigRepository(), []);
  const planRepo = React.useMemo(() => new LocalStorageDidacticPlanRepository(), []);
  const submitUseCase = React.useMemo(() => new SubmeterPlanoUseCase(planRepo, fieldRepo), [planRepo, fieldRepo]);

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // TanStack Query para campos com cache e persistência offline
  const { data: fields = [], isLoading: isLoadingFields } = useQuery({
    queryKey: ['fields-config'],
    queryFn: () => fieldRepo.findAll(),
  });

  // TanStack Query para o plano com cache e persistência offline
  const { data: plan, isLoading: isLoadingPlan } = useQuery({
    queryKey: ['didactic-plan', planId],
    queryFn: async () => {
      let p = await planRepo.findById(planId);
      if (!p) {
        // Mock inicial caso não exista no storage
        p = DidacticPlan.create({
          id: planId,
          disciplinaId: 'dcc-084',
          disciplinaNome: 'Laboratório de Programação Web',
          professorId: 'prof-lazaro',
          professorNome: 'Prof. Dr. Lazaro',
          periodoLetivoId: '2026/1',
          camposValores: {
            ementa: 'Conceitos de arquitetura web, DDD, TDD, Clean Architecture e frameworks modernos.',
            metodologia: 'Aulas práticas em laboratório, desenvolvimento guiado por testes e projetos em grupo.',
          },
        });
        await planRepo.save(p);
      }
      return p;
    },
  });

  const saveMutation = useMutation({
    mutationFn: async ({ values, isSubmissaoFinal }: { values: Record<string, any>; isSubmissaoFinal: boolean }) => {
      const result = await submitUseCase.execute({
        planId,
        disciplinaId: plan?.disciplinaId || 'dcc-084',
        disciplinaNome: plan?.disciplinaNome || 'Laboratório de Programação Web',
        professorId: plan?.professorId || 'prof-lazaro',
        professorNome: plan?.professorNome || 'Prof. Dr. Lazaro',
        periodoLetivoId: plan?.periodoLetivoId || '2026/1',
        camposValores: values,
        isSubmissaoFinal,
      });

      if (!result.success) {
        throw new Error(result.mensagem || 'Falha ao processar operação');
      }

      return result;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['didactic-plan', planId] });
      setNotification({
        type: 'success',
        message: variables.isSubmissaoFinal
          ? 'Plano didático submetido com sucesso! Status atualizado.'
          : 'Rascunho salvo no armazenamento local/offline com sucesso!',
      });
      setTimeout(() => setNotification(null), 5000);
    },
    onError: (err: any) => {
      setNotification({
        type: 'error',
        message: err.message || 'Erro ao salvar plano didático.',
      });
    },
  });

  if (isLoadingFields || isLoadingPlan) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-slate-500 gap-3">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
        <p className="text-sm font-medium">Carregando plano didático e campos configurados...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors gap-1.5"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar para Lista de Planos
        </Link>

        <span className="text-xs text-slate-400 font-mono">ID: {planId}</span>
      </div>

      {notification && (
        <div
          className={`p-4 rounded-xl border flex items-center gap-3 transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          }`}
        >
          {notification.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-rose-600 flex-shrink-0" />
          )}
          <span className="text-sm font-medium">{notification.message}</span>
        </div>
      )}

      <PlanForm
        fields={fields}
        plan={plan}
        isSaving={saveMutation.isPending}
        onSave={(values) => saveMutation.mutate({ values, isSubmissaoFinal: false })}
        onSubmit={(values) => saveMutation.mutate({ values, isSubmissaoFinal: true })}
      />
    </div>
  );
}

