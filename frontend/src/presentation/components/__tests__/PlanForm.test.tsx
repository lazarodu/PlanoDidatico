import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PlanForm } from '../PlanForm';
import { FieldConfig } from '@/domain/value-objects/FieldConfig';
import { DidacticPlan, PlanStatus } from '@/domain/entities/DidacticPlan';

describe('PlanForm Component (Interface UI Test)', () => {
  const fields = [
    FieldConfig.create({
      id: 'f1',
      name: 'ementa',
      label: 'Ementa da Disciplina',
      type: 'textarea',
      required: true,
    }),
    FieldConfig.create({
      id: 'f2',
      name: 'bibliografia',
      label: 'Bibliografia Complementar',
      type: 'textarea',
      required: false,
    }),
  ];

  const mockPlan = DidacticPlan.create({
    id: 'plan-1',
    disciplinaId: 'disc-1',
    disciplinaNome: 'Laboratório Web',
    professorId: 'prof-1',
    professorNome: 'Prof. Carlos',
    periodoLetivoId: '2026-1',
    camposValores: {
      ementa: 'Conceitos de arquitetura web',
    },
    status: PlanStatus.RASCUNHO,
  });

  it('should render form fields dynamically and populate initial values', () => {
    render(<PlanForm fields={fields} plan={mockPlan} onSave={vi.fn()} onSubmit={vi.fn()} />);

    expect(screen.getByLabelText(/Ementa da Disciplina/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Bibliografia Complementar/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('Conceitos de arquitetura web')).toBeInTheDocument();
  });

  it('should trigger onSave callback with updated values', () => {
    const handleSave = vi.fn();
    render(<PlanForm fields={fields} plan={mockPlan} onSave={handleSave} onSubmit={vi.fn()} />);

    const textarea = screen.getByLabelText(/Bibliografia Complementar/i);
    fireEvent.change(textarea, { target: { value: 'Livros recomendados' } });

    const saveButton = screen.getByRole('button', { name: /Salvar Rascunho/i });
    fireEvent.click(saveButton);

    expect(handleSave).toHaveBeenCalledWith(
      expect.objectContaining({
        ementa: 'Conceitos de arquitetura web',
        bibliografia: 'Livros recomendados',
      })
    );
  });
});

