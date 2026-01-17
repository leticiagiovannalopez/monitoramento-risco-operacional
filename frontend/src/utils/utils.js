export function formatDate(isoDate) {
  if (!isoDate) return 'Data inválida';

  try {
    const date = new Date(isoDate);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    return 'Data inválida';
  }
}

export function formatDateShort(isoDate) {
  if (!isoDate) return 'Data inválida';
  
  try {
    const date = new Date(isoDate);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  } catch (error) {
    return 'Data inválida';
  }
}

export function formatCurrency(value) {
  if (value === null || value === undefined) return 'R$ 0,00';
  
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  });
}

export function formatNumber(value) {
  if (value === null || value === undefined) return '0';
  
  return value.toLocaleString('pt-BR');
}

export function groupEventsByDate(eventos) {
  const grouped = {};

  eventos.forEach(evento => {
    const date = formatDateShort(evento.data_evento);
    
    if (!grouped[date]) {
      grouped[date] = {
        dia: date,
        critico: 0,
        alto: 0,
        medio: 0,
        baixo: 0,
        total: 0
      };
    }

    const nivel = evento.nivel_risco.toLowerCase();
    grouped[date][nivel]++;
    grouped[date].total++;
  });

  return Object.values(grouped).sort((a, b) => {
    const dateA = new Date(a.dia.split('/').reverse().join('-'));
    const dateB = new Date(b.dia.split('/').reverse().join('-'));
    return dateA - dateB;
  });
}

export function calculateDistribution(kpis) {
  const total = kpis.total;
  
  if (total === 0) {
    return [
      { nivel: 'Crítico', valor: 0, percentual: 0 },
      { nivel: 'Alto', valor: 0, percentual: 0 },
      { nivel: 'Médio', valor: 0, percentual: 0 },
      { nivel: 'Baixo', valor: 0, percentual: 0 }
    ];
  }

  return [
    {
      nivel: 'Crítico',
      valor: kpis.critico,
      percentual: ((kpis.critico / total) * 100).toFixed(1)
    },
    {
      nivel: 'Alto',
      valor: kpis.alto,
      percentual: ((kpis.alto / total) * 100).toFixed(1)
    },
    {
      nivel: 'Médio',
      valor: kpis.medio,
      percentual: ((kpis.medio / total) * 100).toFixed(1)
    },
    {
      nivel: 'Baixo',
      valor: kpis.baixo,
      percentual: ((kpis.baixo / total) * 100).toFixed(1)
    }
  ];
}

export function normalizeRiskLevel(nivel) {
  if (!nivel) return 'baixo';
  return nivel.toLowerCase();
}
