'use client';

import React, { useState } from 'react';

export default function Home() {
  const [role, setRole] = useState<'professor' | 'coordinator' | 'admin'>('professor');
  const [msg, setMsg] = useState('');

  const [profName, setProfName] = useState('Prof. Ana Silva');
  const [atividade, setAtividade] = useState('Atividades Aritméticas e Provas Práticas');
  const [cronograma, setCronograma] = useState('Semana 1: Intro, Semana 2: DDD');
  const [periodoAno, setPeriodoAno] = useState('2026');
  const [periodoSemestre, setPeriodoSemestre] = useState('1');
  const [dataLimite, setDataLimite] = useState('2026-03-01');
  const [fieldName, setFieldName] = useState('');
  const [fieldType, setFieldType] = useState('textarea');

  const handleProfSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMsg('Plano didático submetido com sucesso! PDF pronto para download.');
  };

  const handleCoordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(`Período Letivo ${periodoAno}.${periodoSemestre} definido com limite em ${dataLimite}.`);
  };

  const handleAdminSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMsg(`Novo campo configurável '${fieldName}' (${fieldType}) criado com sucesso.`);
    setFieldName('');
  };

  return (
    <div style={{ fontFamily: 'sans-serif', margin: 0, padding: 0, backgroundColor: '#f4f6f8', minHeight: '100vh' }}>
      <header style={{ backgroundColor: '#003366', color: '#ffffff', padding: '1rem 2rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.5rem' }}>CEFET-MG — Sistema de Planos Didáticos</h1>
        <p style={{ margin: '0.25rem 0 0 0', opacity: 0.8, fontSize: '0.9rem' }}>
          Gestão descentralizada por perfil (Professor, Coordenador, Admin)
        </p>
      </header>

      <nav style={{ display: 'flex', gap: '1rem', padding: '1rem 2rem', backgroundColor: '#e2e8f0' }}>
        <button
          onClick={() => { setRole('professor'); setMsg(''); }}
          style={{ padding: '0.5rem 1rem', borderRadius: '4px', border: 'none', backgroundColor: role === 'professor' ? '#003366' : '#cbd5e1', color: role === 'professor' ? '#fff' : '#000', cursor: 'pointer' }}
        >
          Visão Professor
        </button>
        <button
          onClick={() => { setRole('coordinator'); setMsg(''); }}
          style={{ padding: '0.5rem 1rem', borderRadius: '4px', border: 'none', backgroundColor: role === 'coordinator' ? '#003366' : '#cbd5e1', color: role === 'coordinator' ? '#fff' : '#000', cursor: 'pointer' }}
        >
          Visão Coordenador
        </button>
        <button
          onClick={() => { setRole('admin'); setMsg(''); }}
          style={{ padding: '0.5rem 1rem', borderRadius: '4px', border: 'none', backgroundColor: role === 'admin' ? '#003366' : '#cbd5e1', color: role === 'admin' ? '#fff' : '#000', cursor: 'pointer' }}
        >
          Visão Administrador
        </button>
      </nav>

      <main style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        {msg && (
          <div style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '1rem', borderRadius: '6px', marginBottom: '1.5rem' }}>
            {msg}
          </div>
        )}

        {role === 'professor' && (
          <section style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h2>Submeter Plano Didático (UC1 / RF01 / RF03)</h2>
            <form onSubmit={handleProfSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Docente Responsável (Campo Fixo)</label>
                <input type="text" value={profName} onChange={(e) => setProfName(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Atividades Avaliativas (Campo Variável)</label>
                <textarea rows={3} value={atividade} onChange={(e) => setAtividade(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Cronograma Detalhado (Campo Variável)</label>
                <textarea rows={3} value={cronograma} onChange={(e) => setCronograma(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="submit" style={{ backgroundColor: '#003366', color: '#ffffff', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  Submeter Plano
                </button>
                <button type="button" onClick={() => window.open('/api/plans/1/pdf', '_blank')} style={{ backgroundColor: '#2563eb', color: '#ffffff', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  Gerar PDF
                </button>
              </div>
            </form>
          </section>
        )}

        {role === 'coordinator' && (
          <section style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h2>Gestão do Período e Professores (UC11 / UC12 / UC13 / RF07 / RF09 / RF11)</h2>
            <form onSubmit={handleCoordSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
              <h3>Definir Período Letivo</h3>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Ano</label>
                  <input type="number" value={periodoAno} onChange={(e) => setPeriodoAno(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Semestre</label>
                  <input type="number" value={periodoSemestre} onChange={(e) => setPeriodoSemestre(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
                </div>
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Data Limite para Entrega do Plano</label>
                <input type="date" value={dataLimite} onChange={(e) => setDataLimite(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
              <button type="submit" style={{ backgroundColor: '#003366', color: '#ffffff', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', cursor: 'pointer', alignSelf: 'flex-start' }}>
                Salvar Período Letivo
              </button>
            </form>

            <div>
              <h3>Importar Lista de Professores via CSV (RF07)</h3>
              <input type="file" accept=".csv" onChange={() => setMsg('CSV importado! 5 novos professores cadastrados.')} style={{ marginBottom: '1rem' }} />
            </div>
          </section>
        )}

        {role === 'admin' && (
          <section style={{ backgroundColor: '#ffffff', padding: '1.5rem', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h2>Gerenciar Campos do Formulário e Canais (UC8 / UC16 / RF04 / RF12)</h2>
            <form onSubmit={handleAdminSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Nome do Novo Campo</label>
                <input type="text" value={fieldName} onChange={(e) => setFieldName(e.target.value)} placeholder="Ex: recursos_didaticos" required style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '0.5rem' }}>Tipo do Campo</label>
                <select value={fieldType} onChange={(e) => setFieldType(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}>
                  <option value="textarea">Textarea (Texto Multilinha)</option>
                  <option value="text">Input Text</option>
                  <option value="date">Data</option>
                  <option value="select">Seleção</option>
                </select>
              </div>
              <button type="submit" style={{ backgroundColor: '#003366', color: '#ffffff', padding: '0.75rem 1.5rem', border: 'none', borderRadius: '4px', cursor: 'pointer', alignSelf: 'flex-start' }}>
                Adicionar Campo
              </button>
            </form>
          </section>
        )}
      </main>
    </div>
  );
}
