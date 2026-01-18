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
  const colors = {
    critico: '#ef4444',
    alto: '#f97316',
    medio: '#eab308',
    baixo: '#22c55e'
  };

  return [
    { name: 'Crítico', value: kpis.critico || 0, color: colors.critico },
    { name: 'Alto', value: kpis.alto || 0, color: colors.alto },
    { name: 'Médio', value: kpis.medio || 0, color: colors.medio },
    { name: 'Baixo', value: kpis.baixo || 0, color: colors.baixo }
  ];
}

export function normalizeRiskLevel(nivel) {
  if (!nivel) return 'baixo';
  return nivel.toLowerCase();
}
