'use client';

import React, { useState } from 'react';
import { FieldConfig } from '@/domain/value-objects/FieldConfig';
import { DidacticPlan, PlanStatus } from '@/domain/entities/DidacticPlan';
import { Button } from '@/shared/components/ui/Button';
import { Input } from '@/shared/components/ui/Input';
import { Textarea } from '@/shared/components/ui/Textarea';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/shared/components/ui/Card';
import { Badge } from '@/shared/components/ui/Badge';
import { Save, Send, CheckCircle2, AlertCircle } from 'lucide-react';

export interface PlanFormProps {
  fields: FieldConfig[];
  plan?: DidacticPlan;
  onSave: (values: Record<string, any>) => void;
  onSubmit: (values: Record<string, any>) => void;
  isSaving?: boolean;
}

export function PlanForm({ fields, plan, onSave, onSubmit, isSaving }: PlanFormProps) {
  const [formData, setFormData] = useState<Record<string, any>>(plan?.camposValores || {});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const isReadOnly = plan?.status === PlanStatus.APROVADO;

  const handleChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSaveDraft = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleSubmitFinal = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: Record<string, string> = {};

    for (const field of fields) {
      const err = field.validate(formData[field.name]);
      if (err) {
        newErrors[field.name] = err;
      }
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit(formData);
  };

  return (
    <Card className="max-w-4xl mx-auto shadow-md border-slate-200">
      <CardHeader className="bg-slate-50/50 rounded-t-xl">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-xl text-slate-800">
              {plan?.disciplinaNome || 'Plano Didático Institucional'}
            </CardTitle>
            <CardDescription className="mt-1 text-slate-600">
              Professor(a): <strong className="text-slate-700">{plan?.professorNome || 'Docente Responsável'}</strong> • Período: {plan?.periodoLetivoId || '2026/1'}
            </CardDescription>
          </div>
          <Badge status={plan?.status || PlanStatus.RASCUNHO} />
        </div>
      </CardHeader>

      <form onSubmit={handleSubmitFinal}>
        <CardContent className="space-y-6 pt-6">
          {Object.keys(errors).length > 0 && (
            <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
              <div>
                <p className="font-semibold text-sm">Existem pendências no preenchimento:</p>
                <ul className="text-xs list-disc list-inside mt-1 space-y-0.5">
                  {Object.values(errors).map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {fields.map((field) => {
            const value = formData[field.name] ?? '';
            const error = errors[field.name];

            if (field.type === 'textarea') {
              return (
                <Textarea
                  key={field.id}
                  id={field.name}
                  label={field.label}
                  required={field.required}
                  value={value}
                  error={error}
                  disabled={isReadOnly || isSaving}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  placeholder={`Insira ${field.label.toLowerCase()}...`}
                />
              );
            }

            return (
              <Input
                key={field.id}
                id={field.name}
                type={field.type === 'number' ? 'number' : 'text'}
                label={field.label}
                required={field.required}
                value={value}
                error={error}
                disabled={isReadOnly || isSaving}
                onChange={(e) => handleChange(field.name, e.target.value)}
                placeholder={`Insira ${field.label.toLowerCase()}...`}
              />
            );
          })}
        </CardContent>

        <CardFooter className="flex items-center justify-between gap-4 bg-slate-50/50 py-4 px-6 border-t border-slate-100 rounded-b-xl">
          <Button
            type="button"
            variant="outline"
            disabled={isReadOnly || isSaving}
            onClick={handleSaveDraft}
          >
            <Save className="w-4 h-4 text-slate-500" />
            Salvar Rascunho
          </Button>

          <Button
            type="submit"
            variant="primary"
            disabled={isReadOnly || isSaving}
          >
            <Send className="w-4 h-4" />
            Submeter Plano Didático
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

