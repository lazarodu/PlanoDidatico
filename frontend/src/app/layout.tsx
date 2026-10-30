import type { Metadata } from 'next';
import './globals.css';
import { ReactQueryProvider } from '@/shared/providers/ReactQueryProvider';
import { NavigationHeader } from '@/presentation/components/NavigationHeader';

export const metadata: Metadata = {
  title: 'Sistema de Planos Didáticos - CEFET-MG',
  description:
    'Plataforma institucional de submissão e homologação de Planos Didáticos com arquitetura DDD, Clean Architecture e suporte Offline-First.',
  keywords: ['Plano Didático', 'CEFET-MG', 'Clean Architecture', 'DDD', 'TDD', 'Next.js 16'],
  authors: [{ name: 'CEFET-MG' }],
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    title: 'Sistema de Planos Didáticos - CEFET-MG',
    description: 'Gestão de Planos Didáticos por Período Letivo',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-slate-50 text-slate-900 antialiased flex flex-col">
        <ReactQueryProvider>
          <NavigationHeader />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
            <p>© 2026 CEFET-MG - Sistema de Gestão Acadêmica e Planos Didáticos.</p>
            <p className="mt-1 text-slate-400">Implementado com Next.js 16, Turbopack, DDD, Clean Architecture e TDD.</p>
          </footer>
        </ReactQueryProvider>
      </body>
    </html>
  );
}
