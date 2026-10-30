import React from 'react';
import { cn } from '@/shared/lib/utils';
import { PlanStatus } from '@/domain/entities/DidacticPlan';

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status?: PlanStatus | string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

export function Badge({ className, status, variant = 'default', children, ...props }: BadgeProps) {
  let badgeVariant = variant;

  if (status) {
    switch (status) {
      case PlanStatus.APROVADO:
        badgeVariant = 'success';
        break;
      case PlanStatus.SUBMETIDO:
        badgeVariant = 'info';
        break;
      case PlanStatus.REJEITADO:
        badgeVariant = 'danger';
        break;
      case PlanStatus.RASCUNHO:
      default:
        badgeVariant = 'warning';
        break;
    }
  }

  const variants = {
    default: 'bg-slate-100 text-slate-800 border-slate-200',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors',
        variants[badgeVariant],
        className
      )}
      {...props}
    >
      {children || status}
    </span>
  );
}

