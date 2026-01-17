function generateTimelineData(days) {
  const data = [];
  const today = new Date();

  const dailyAvg = {
    critico: 184 / 30,
    alto: 494 / 30,
    medio: 1447 / 30,
    baixo: 2875 / 30
  };

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);

    const variance = () => 0.7 + Math.random() * 0.6;

    const critico = Math.round(dailyAvg.critico * variance());
    const alto = Math.round(dailyAvg.alto * variance());
    const medio = Math.round(dailyAvg.medio * variance());
    const baixo = Math.round(dailyAvg.baixo * variance());

    data.push({
      dia: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
      critico,
      alto,
      medio,
      baixo,
      total: critico + alto + medio + baixo
    });
  }

  return data;
}

function calculateKPIs(timelineData) {
  return timelineData.reduce((acc, day) => ({
    total: acc.total + day.total,
    critico: acc.critico + day.critico,
    alto: acc.alto + day.alto,
    medio: acc.medio + day.medio,
    baixo: acc.baixo + day.baixo
  }), { total: 0, critico: 0, alto: 0, medio: 0, baixo: 0 });
}

function generateDistributionData(kpis) {
  return [
    { name: 'Crítico', value: kpis.critico, color: '#EF4444' },
    { name: 'Alto', value: kpis.alto, color: '#F97316' },
    { name: 'Médio', value: kpis.medio, color: '#FBBF24' },
    { name: 'Baixo', value: kpis.baixo, color: '#10B981' }
  ];
}

export const periodData = {
  '7d': {
    timeline: [
      { dia: '09/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '10/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '11/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '12/01', critico: 9, alto: 20, medio: 56, baixo: 105, total: 190 },
      { dia: '13/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '14/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '15/01', critico: 6, alto: 16, medio: 49, baixo: 99, total: 170 }
    ],
    kpis: { total: 1242, critico: 51, alto: 126, medio: 365, baixo: 700 }
  },
  '15d': {
    timeline: [
      { dia: '01/01', critico: 6, alto: 17, medio: 49, baixo: 97, total: 169 },
      { dia: '02/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '03/01', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '04/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '05/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '06/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '07/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '08/01', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '09/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '10/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '11/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '12/01', critico: 9, alto: 20, medio: 56, baixo: 105, total: 190 },
      { dia: '13/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '14/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '15/01', critico: 6, alto: 16, medio: 49, baixo: 99, total: 170 }
    ],
    kpis: { total: 2517, critico: 101, alto: 260, medio: 760, baixo: 1396 }
  },
  '30d': {
    timeline: [
      { dia: '17/12', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '18/12', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '19/12', critico: 4, alto: 14, medio: 44, baixo: 88, total: 150 },
      { dia: '20/12', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '21/12', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '22/12', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '23/12', critico: 6, alto: 17, medio: 49, baixo: 97, total: 169 },
      { dia: '24/12', critico: 4, alto: 13, medio: 40, baixo: 82, total: 139 },
      { dia: '25/12', critico: 3, alto: 11, medio: 36, baixo: 72, total: 122 },
      { dia: '26/12', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '27/12', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '28/12', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '29/12', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '30/12', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '31/12', critico: 4, alto: 14, medio: 44, baixo: 88, total: 150 },
      { dia: '01/01', critico: 6, alto: 17, medio: 49, baixo: 97, total: 169 },
      { dia: '02/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '03/01', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '04/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '05/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '06/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '07/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '08/01', critico: 5, alto: 15, medio: 46, baixo: 92, total: 158 },
      { dia: '09/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '10/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '11/01', critico: 6, alto: 16, medio: 48, baixo: 96, total: 166 },
      { dia: '12/01', critico: 9, alto: 20, medio: 56, baixo: 105, total: 190 },
      { dia: '13/01', critico: 7, alto: 18, medio: 52, baixo: 98, total: 175 },
      { dia: '14/01', critico: 8, alto: 19, medio: 54, baixo: 102, total: 183 },
      { dia: '15/01', critico: 6, alto: 16, medio: 49, baixo: 99, total: 170 }
    ],
    kpis: { total: 5000, critico: 184, alto: 494, medio: 1447, baixo: 2875 }
  },
  '3m': {
    timeline: [
      { dia: 'Sem 1', critico: 42, alto: 112, medio: 336, baixo: 672, total: 1162 },
      { dia: 'Sem 2', critico: 38, alto: 105, medio: 315, baixo: 630, total: 1088 },
      { dia: 'Sem 3', critico: 45, alto: 118, medio: 354, baixo: 708, total: 1225 },
      { dia: 'Sem 4', critico: 40, alto: 108, medio: 324, baixo: 648, total: 1120 },
      { dia: 'Sem 5', critico: 48, alto: 125, medio: 375, baixo: 750, total: 1298 },
      { dia: 'Sem 6', critico: 35, alto: 98, medio: 294, baixo: 588, total: 1015 },
      { dia: 'Sem 7', critico: 52, alto: 132, medio: 396, baixo: 792, total: 1372 },
      { dia: 'Sem 8', critico: 44, alto: 115, medio: 345, baixo: 690, total: 1194 },
      { dia: 'Sem 9', critico: 39, alto: 102, medio: 306, baixo: 612, total: 1059 },
      { dia: 'Sem 10', critico: 50, alto: 128, medio: 384, baixo: 768, total: 1330 },
      { dia: 'Sem 11', critico: 46, alto: 120, medio: 360, baixo: 720, total: 1246 },
      { dia: 'Sem 12', critico: 41, alto: 110, medio: 330, baixo: 660, total: 1141 }
    ],
    kpis: { total: 14250, critico: 520, alto: 1373, medio: 4119, baixo: 8238 }
  },
  '6m': {
    timeline: [
      { dia: 'Ago', critico: 156, alto: 412, medio: 1236, baixo: 2472, total: 4276 },
      { dia: 'Set', critico: 168, alto: 445, medio: 1335, baixo: 2670, total: 4618 },
      { dia: 'Out', critico: 172, alto: 458, medio: 1374, baixo: 2748, total: 4752 },
      { dia: 'Nov', critico: 148, alto: 395, medio: 1185, baixo: 2370, total: 4098 },
      { dia: 'Dez', critico: 180, alto: 478, medio: 1434, baixo: 2868, total: 4960 },
      { dia: 'Jan', critico: 184, alto: 494, medio: 1447, baixo: 2875, total: 5000 }
    ],
    kpis: { total: 27704, critico: 1008, alto: 2682, medio: 8011, baixo: 16003 }
  },
  '12m': {
    timeline: [
      { dia: 'Fev', critico: 145, alto: 385, medio: 1155, baixo: 2310, total: 3995 },
      { dia: 'Mar', critico: 162, alto: 432, medio: 1296, baixo: 2592, total: 4482 },
      { dia: 'Abr', critico: 158, alto: 420, medio: 1260, baixo: 2520, total: 4358 },
      { dia: 'Mai', critico: 175, alto: 465, medio: 1395, baixo: 2790, total: 4825 },
      { dia: 'Jun', critico: 168, alto: 448, medio: 1344, baixo: 2688, total: 4648 },
      { dia: 'Jul', critico: 155, alto: 412, medio: 1236, baixo: 2472, total: 4275 },
      { dia: 'Ago', critico: 156, alto: 412, medio: 1236, baixo: 2472, total: 4276 },
      { dia: 'Set', critico: 168, alto: 445, medio: 1335, baixo: 2670, total: 4618 },
      { dia: 'Out', critico: 172, alto: 458, medio: 1374, baixo: 2748, total: 4752 },
      { dia: 'Nov', critico: 148, alto: 395, medio: 1185, baixo: 2370, total: 4098 },
      { dia: 'Dez', critico: 180, alto: 478, medio: 1434, baixo: 2868, total: 4960 },
      { dia: 'Jan', critico: 184, alto: 494, medio: 1447, baixo: 2875, total: 5000 }
    ],
    kpis: { total: 54287, critico: 1971, alto: 5244, medio: 15697, baixo: 31375 }
  }
};

export function getDataByPeriod(period) {
  const data = periodData[period] || periodData['30d'];
  return {
    kpis: data.kpis,
    timeline: data.timeline,
    distribution: generateDistributionData(data.kpis)
  };
}

export const periodLabels = {
  '7d': 'Últimos 7 dias',
  '15d': 'Últimos 15 dias',
  '30d': 'Últimos 30 dias',
  '3m': 'Últimos 3 meses',
  '6m': 'Últimos 6 meses',
  '12m': 'Últimos 12 meses'
};

export const kpiData = periodData['30d'].kpis;
export const timelineData = periodData['30d'].timeline;
export const distributionData = generateDistributionData(kpiData);

const gerarDataRecente = (diasAtras) => {
  const data = new Date();
  data.setDate(data.getDate() - diasAtras);
  return data.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const recentEvents = [
  {
    id: 1,
    data: gerarDataRecente(0),
    nivel_risco: 'Crítico',
    tipo_evento: 'Fraude Detectada',
    impacto_financeiro: 'R$ 125.000,00',
    clientes_afetados: 12
  },
  {
    id: 2,
    data: gerarDataRecente(0),
    nivel_risco: 'Alto',
    tipo_evento: 'Falha de Sistema',
    impacto_financeiro: 'R$ 45.200,00',
    clientes_afetados: 234
  },
  {
    id: 3,
    data: gerarDataRecente(1),
    nivel_risco: 'Médio',
    tipo_evento: 'Erro de Processamento',
    impacto_financeiro: 'R$ 8.500,00',
    clientes_afetados: 45
  },
  {
    id: 4,
    data: gerarDataRecente(1),
    nivel_risco: 'Baixo',
    tipo_evento: 'Timeout de Transação',
    impacto_financeiro: 'R$ 1.200,00',
    clientes_afetados: 8
  },
  {
    id: 5,
    data: gerarDataRecente(2),
    nivel_risco: 'Alto',
    tipo_evento: 'Violação de Compliance',
    impacto_financeiro: 'R$ 78.900,00',
    clientes_afetados: 156
  },
  {
    id: 6,
    data: gerarDataRecente(2),
    nivel_risco: 'Crítico',
    tipo_evento: 'Acesso Não Autorizado',
    impacto_financeiro: 'R$ 250.000,00',
    clientes_afetados: 1
  },
  {
    id: 7,
    data: gerarDataRecente(3),
    nivel_risco: 'Médio',
    tipo_evento: 'Falha de Integração',
    impacto_financeiro: 'R$ 15.600,00',
    clientes_afetados: 89
  },
  {
    id: 8,
    data: gerarDataRecente(3),
    nivel_risco: 'Baixo',
    tipo_evento: 'Inconsistência de Dados',
    impacto_financeiro: 'R$ 2.300,00',
    clientes_afetados: 23
  },
  {
    id: 9,
    data: gerarDataRecente(4),
    nivel_risco: 'Alto',
    tipo_evento: 'Erro de Conciliação',
    impacto_financeiro: 'R$ 56.700,00',
    clientes_afetados: 312
  },
  {
    id: 10,
    data: gerarDataRecente(5),
    nivel_risco: 'Médio',
    tipo_evento: 'Indisponibilidade',
    impacto_financeiro: 'R$ 12.400,00',
    clientes_afetados: 567
  }
];

export const riskColors = {
  Crítico: {
    bg: 'var(--color-risk-critical-bg)',
    border: 'var(--color-risk-critical-border)',
    text: 'var(--color-risk-critical)',
    hex: '#EF4444'
  },
  Alto: {
    bg: 'var(--color-risk-high-bg)',
    border: 'var(--color-risk-high-border)',
    text: 'var(--color-risk-high)',
    hex: '#F97316'
  },
  Médio: {
    bg: 'var(--color-risk-medium-bg)',
    border: 'var(--color-risk-medium-border)',
    text: 'var(--color-risk-medium)',
    hex: '#FBBF24'
  },
  Baixo: {
    bg: 'var(--color-risk-low-bg)',
    border: 'var(--color-risk-low-border)',
    text: 'var(--color-risk-low)',
    hex: '#10B981'
  }
};
