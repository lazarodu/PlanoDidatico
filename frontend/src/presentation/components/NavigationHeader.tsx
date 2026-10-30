import React from 'react';
import Link from 'next/link';
import { BookOpen, Calendar, Settings, ShieldCheck, WifiOff, FileText, CheckCircle2 } from 'lucide-react';

export function NavigationHeader() {
  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-slate-900 tracking-tight text-lg block leading-tight">
              Sistema de Planos Didáticos
            </span>
            <span className="text-xs text-slate-500 font-medium">CEFET-MG • Clean Architecture & DDD</span>
          </div>
        </div>

        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/"
            className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-blue-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <FileText className="w-4 h-4 text-slate-400" />
            Planos
          </Link>
          <Link
            href="/atribuicoes"
            className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-blue-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Calendar className="w-4 h-4 text-slate-400" />
            Atribuições & Carga (RF11)
          </Link>
          <Link
            href="/campos"
            className="px-3 py-2 text-sm font-medium text-slate-700 hover:text-blue-600 hover:bg-slate-50 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            Configurar Formulário (RF04)
          </Link>
        </nav>

        <div className="hidden md:flex items-center gap-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full font-medium">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
          Offline-First Ativo
        </div>
      </div>
    </header>
  );
}

