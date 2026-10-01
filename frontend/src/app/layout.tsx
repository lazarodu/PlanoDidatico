export const metadata = {
  title: 'CEFET-MG — Sistema de Planos Didáticos',
  description: 'Gestão de Planos Didáticos',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body style={{ margin: 0, padding: 0 }}>{children}</body>
    </html>
  )
}
