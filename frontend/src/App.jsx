import { useState, useEffect } from 'react'
import axios from 'axios'
import './colors.css'

function App() {
  const [eventos, setEventos] = useState([])
  const [stats, setStats] = useState({
    total: 0,
    critico: 0,
    alto: 0,
    medio: 0,
    baixo: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchEventos()
  }, [])

  const fetchEventos = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/eventos')
      setEventos(response.data.eventos)
      
      const total = response.data.total
      const critico = response.data.eventos.filter(e => e.nivel_risco === 'critico').length
      const alto = response.data.eventos.filter(e => e.nivel_risco === 'alto').length
      const medio = response.data.eventos.filter(e => e.nivel_risco === 'medio').length
      const baixo = response.data.eventos.filter(e => e.nivel_risco === 'baixo').length
      
      setStats({ total, critico, alto, medio, baixo })
      setLoading(false)
    } catch (error) {
      console.error('Erro ao buscar eventos:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '24px',
        color: 'var(--primary)'
      }}>
        Carregando...
      </div>
    )
  }

  return (
    <div style={{
      minHeight: '100vh',
      padding: '3rem 5%',
      background: 'var(--background)',
      width: '100%'
    }}>
      {/* Header */}
      <header style={{
        marginBottom: '3rem',
        borderBottom: '1px solid var(--border)',
        paddingBottom: '1.5rem'
      }}>
        <h1 style={{
          fontSize: '2rem',
          fontWeight: '300',
          background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '0.5rem',
          letterSpacing: '-0.03em'
        }}>
          Monitoramento de Risco Operacional
        </h1>
        <p style={{ 
          color: 'var(--text-secondary)',
          fontSize: '0.95rem',
          fontWeight: '300',
          letterSpacing: '-0.01em'
        }}>
          Sistema de análise com IA · Yoyo 💜
        </p>
      </header>

      {/* KPIs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '2rem',
        marginBottom: '3rem'
      }}>
        <KPICard 
          title="Total de Eventos"
          value={stats.total}
          color="var(--primary)"
        />
        <KPICard 
          title="🔴 Críticos"
          value={stats.critico}
          color="var(--risk-critico)"
        />
        <KPICard 
          title="🟠 Altos"
          value={stats.alto}
          color="var(--risk-alto)"
        />
        <KPICard 
          title="🟡 Médios"
          value={stats.medio}
          color="var(--risk-medio)"
        />
        <KPICard 
          title="🟢 Baixos"
          value={stats.baixo}
          color="var(--risk-baixo)"
        />
      </div>

      {/* Últimos eventos */}
      <div style={{
        background: 'linear-gradient(135deg, var(--surface) 0%, rgba(30, 41, 59, 0.4) 100%)',
        padding: '2rem',
        borderRadius: '20px',
        border: '1px solid var(--border)',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)'
      }}>
        <h2 style={{
          background: 'linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '1.5rem',
          fontSize: '1.75rem',
          fontWeight: '500',
          letterSpacing: '-0.02em'
        }}>
          📊 Últimos Eventos
        </h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)' }}>
                <th style={tableHeaderStyle}>Data</th>
                <th style={tableHeaderStyle}>Nível</th>
                <th style={tableHeaderStyle}>Tipo</th>
                <th style={tableHeaderStyle}>Impacto (R$)</th>
                <th style={tableHeaderStyle}>Clientes</th>
              </tr>
            </thead>
            <tbody>
              {eventos.slice(0, 10).map((evento, index) => (
                <tr key={index} style={{
                  borderBottom: '1px solid var(--border)',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(99, 102, 241, 0.08)'
                  e.currentTarget.style.transform = 'scale(1.01)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.transform = 'scale(1)'
                }}>
                  <td style={tableCellStyle}>
                    {new Date(evento.data_evento).toLocaleDateString('pt-BR')}
                  </td>
                  <td style={tableCellStyle}>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.875rem',
                      fontWeight: 'bold',
                      background: getNivelColor(evento.nivel_risco),
                      color: '#fff'
                    }}>
                      {evento.nivel_risco.toUpperCase()}
                    </span>
                  </td>
                  <td style={tableCellStyle}>{evento.tipo_evento}</td>
                  <td style={tableCellStyle}>
                    R$ {evento.impacto_financeiro.toLocaleString('pt-BR')}
                  </td>
                  <td style={tableCellStyle}>
                    {evento.clientes_afetados.toLocaleString('pt-BR')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function KPICard({ title, value, color }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, var(--surface) 0%, rgba(30, 41, 59, 0.6) 100%)',
      padding: '2rem',
      borderRadius: '20px',
      border: '1px solid var(--border)',
      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
      cursor: 'default',
      position: 'relative',
      overflow: 'hidden',
      backdropFilter: 'blur(10px)'
    }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-6px) scale(1.02)'
      e.currentTarget.style.boxShadow = `0 20px 40px ${color}33, 0 0 0 1px ${color}44`
      e.currentTarget.style.borderColor = color
      e.currentTarget.style.background = `linear-gradient(135deg, ${color}15 0%, var(--surface) 100%)`
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0) scale(1)'
      e.currentTarget.style.boxShadow = 'none'
      e.currentTarget.style.borderColor = 'var(--border)'
      e.currentTarget.style.background = 'linear-gradient(135deg, var(--surface) 0%, rgba(30, 41, 59, 0.6) 100%)'
    }}>
      <div style={{
        position: 'absolute',
        top: '0',
        right: '0',
        width: '100px',
        height: '100px',
        background: `radial-gradient(circle, ${color}20 0%, transparent 70%)`,
        borderRadius: '50%',
        transform: 'translate(30%, -30%)',
        pointerEvents: 'none'
      }}></div>
      <div style={{
        color: 'var(--text-secondary)',
        fontSize: '0.75rem',
        marginBottom: '1rem',
        fontWeight: '600',
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        opacity: '0.9'
      }}>
        {title}
      </div>
      <div style={{
        fontSize: '2.75rem',
        fontWeight: '400',
        color: color,
        letterSpacing: '-0.02em',
        lineHeight: '1'
      }}>
        {value.toLocaleString('pt-BR')}
      </div>
    </div>
  )
}

function getNivelColor(nivel) {
  const colors = {
    'critico': 'var(--risk-critico)',
    'alto': 'var(--risk-alto)',
    'medio': 'var(--risk-medio)',
    'baixo': 'var(--risk-baixo)'
  }
  return colors[nivel] || 'var(--text-secondary)'
}

const tableHeaderStyle = {
  padding: '1.25rem 1rem',
  textAlign: 'left',
  color: 'var(--text-secondary)',
  fontWeight: '600',
  fontSize: '0.8125rem',
  letterSpacing: '0.05em',
  textTransform: 'uppercase'
}

const tableCellStyle = {
  padding: '1.25rem 1rem',
  color: 'var(--text-primary)',
  fontSize: '0.9375rem',
  letterSpacing: '0.01em'
}

export default App