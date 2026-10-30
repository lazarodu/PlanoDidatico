'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/shared/components/ui/Card';
import { Button } from '@/shared/components/ui/Button';
import { Input } from '@/shared/components/ui/Input';
import { FieldConfig, FieldType } from '@/domain/value-objects/FieldConfig';
import { LocalStorageFieldConfigRepository } from '@/infrastructure/repositories/LocalStorageFieldConfigRepository';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings, Plus, Trash2, CheckCircle2 } from 'lucide-react';

export default function CamposConfigPage() {
  const queryClient = useQueryClient();
  const repo = React.useMemo(() => new LocalStorageFieldConfigRepository(), []);

  const [label, setLabel] = useState('');
  const [name, setName] = useState('');
  const [type, setType] = useState<FieldType>('textarea');
  const [required, setRequired] = useState(true);
  const [msg, setMsg] = useState<string | null>(null);

  const { data: fields = [], isLoading } = useQuery({
    queryKey: ['fields-config'],
    queryFn: () => repo.findAll(),
  });

  const addMutation = useMutation({
    mutationFn: async (novoCampo: FieldConfig) => {
      await repo.save(novoCampo);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields-config'] });
      setLabel('');
      setName('');
      setMsg('Campo adicionado com sucesso!');
      setTimeout(() => setMsg(null), 4000);
    },
  });

  const removeMutation = useMutation({
    mutationFn: async (id: string) => {
      await repo.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fields-config'] });
      setMsg('Campo removido com sucesso!');
      setTimeout(() => setMsg(null), 4000);
    },
  });

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !label) return;
    const campo = FieldConfig.create({
      id: `field-${Date.now()}`,
      name: name.trim().toLowerCase().replace(/\s+/g, '_'),
      label: label.trim(),
      type,
      required,
      order: fields.length + 1,
    });
    addMutation.mutate(campo);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Settings className="w-6 h-6 text-blue-600" />
          Gerenciamento de Campos Dinâmicos (RF04 - Administrador)
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Adicione ou configure os campos obrigatórios/opcionais do formulário de Plano Didático em conformidade com as diretrizes do CEFET-MG.
        </p>
      </div>

      {msg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-sm flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          {msg}
        </div>
      )}

      {/* Formulário de Criação de Campo */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Novo Campo de Formulário</CardTitle>
          <CardDescription className="text-xs">
            Campos adicionados são automaticamente sincronizados com o editor de planos didáticos.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Rótulo Visível (Label)"
                placeholder="Ex: Metodologia e Tecnologias"
                value={label}
                onChange={(e) => {
                  setLabel(e.target.value);
                  if (!name) {
                    setName(e.target.value.toLowerCase().replace(/[^a-z0-9]/g, '_'));
                  }
                }}
                required
              />
              <Input
                label="Identificador Interno (Name)"
                placeholder="Ex: metodologia_tecnologias"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">Tipo do Campo</label>
                <select
                  className="w-full h-10 px-3 py-2 rounded-md border border-slate-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={type}
                  onChange={(e) => setType(e.target.value as FieldType)}
                >
                  <option value="textarea">Área de Texto (Textarea)</option>
                  <option value="text">Texto Curto (Text)</option>
                  <option value="number">Numérico (Number)</option>
                </select>
              </div>

              <div className="flex items-center gap-2 pt-6">
                <input
                  type="checkbox"
                  id="required"
                  checked={required}
                  onChange={(e) => setRequired(e.target.checked)}
                  className="h-4 w-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500"
                />
                <label htmlFor="required" className="text-sm font-medium text-slate-700 cursor-pointer">
                  Campo Obrigatório na Submissão
                </label>
              </div>
            </div>

            <Button type="submit" variant="primary" className="mt-2" disabled={addMutation.isPending}>
              <Plus className="w-4 h-4 mr-1.5" />
              Adicionar Campo ao Sistema
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Lista de Campos Configurados */}
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="text-base">Campos Ativos no Formulário ({fields.length})</CardTitle>
          <CardDescription className="text-xs">Campos que os docentes deverão preencher</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-slate-100 border border-slate-200 rounded-lg overflow-hidden">
            {fields.map((f) => (
              <div key={f.id} className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div>
                  <div className="flex items-center gap-2">
                    <strong className="text-sm text-slate-800">{f.label}</strong>
                    {f.required && (
                      <span className="text-[10px] bg-red-50 text-red-600 border border-red-200 px-1.5 py-0.5 rounded font-semibold">
                        Obrigatório
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    Nome: {f.name} • Tipo: {f.type}
                  </p>
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  className="text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                  onClick={() => removeMutation.mutate(f.id)}
                  title="Remover campo"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

