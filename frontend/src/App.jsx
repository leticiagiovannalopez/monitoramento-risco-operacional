import { useState, useMemo } from 'react';
import {
  Header,
  KPICards,
  TimelineChart,
  DistributionChart,
  EventsTable,
  DateFilter,
  ChatBot
} from './components';
import { useEvents } from './hooks/useEvents';
import { groupEventsByDate, calculateDistribution } from './utils/utils';
import styles from './App.module.css';

function calcularDatasDoPeríodo(periodo) {
  const hoje = new Date();
  const dataFim = hoje.toISOString().split('T')[0];
  let dataInicio;

  const diasMap = {
    '7d': 7,
    '15d': 15,
    '30d': 30,
    '3m': 90,
    '6m': 180,
    '12m': 365
  };

  const dias = diasMap[periodo] || 30;
  const dataInicioDate = new Date(hoje);
  dataInicioDate.setDate(dataInicioDate.getDate() - dias);
  dataInicio = dataInicioDate.toISOString().split('T')[0];

  return { data_inicio: dataInicio, data_fim: dataFim };
}

function App() {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedDate, setSelectedDate] = useState('');

  const filters = useMemo(() => {
    if (selectedDate) {
      return { data_inicio: selectedDate, data_fim: selectedDate };
    }
    return calcularDatasDoPeríodo(selectedPeriod);
  }, [selectedPeriod, selectedDate]);
  const { eventos, loading, error, kpis } = useEvents(filters);
  const timelineData = groupEventsByDate(eventos);
  const distributionData = calculateDistribution(kpis);

  const formattedDate = selectedDate
    ? new Date(selectedDate + 'T00:00:00').toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric'
      })
    : null;

  if (loading) {
    return (
      <div className={styles.app}>
        <Header />
        <main className={styles.main}>
          <div className={styles.container}>
            <div className={styles.loadingContainer}>
              <div className={styles.spinner}></div>
              <p>Carregando dados do backend...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.app}>
        <Header />
        <main className={styles.main}>
          <div className={styles.container}>
            <div className={styles.errorContainer}>
              <h2> Erro ao carregar dados</h2>
              <p>{error}</p>
              <p className={styles.errorHint}>
                Verifique se o backend está rodando em http://127.0.0.1:8000
              </p>
              <button 
                className={styles.retryButton}
                onClick={() => window.location.reload()}
              >
                Tentar novamente
              </button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className={styles.app}>
      <Header />

      <main className={styles.main}>
        <div className={styles.container}>
          <DateFilter
            selectedPeriod={selectedPeriod}
            onPeriodChange={setSelectedPeriod}
            selectedDate={selectedDate}
            onDateChange={setSelectedDate}
          />

          {selectedDate && (
            <div className={styles.selectedDateBanner}>
              <span>Visualizando eventos de: <strong>{formattedDate}</strong></span>
              <button onClick={() => setSelectedDate('')}>Limpar filtro</button>
            </div>
          )}

          <KPICards data={kpis} />

          <section className={styles.chartsGrid}>
            <TimelineChart data={timelineData} periodLabel="Últimos 30 dias" />
            <DistributionChart data={distributionData} total={kpis.total} />
          </section>

          <section className={styles.tableSection}>
            <EventsTable eventos={eventos} selectedDate={selectedDate} />
          </section>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>
          Yoyo · Sistema de Monitoramento de Risco Operacional
          <span className={styles.separator}>•</span>
          <span className={styles.version}>v1.0.0</span>
          <span className={styles.separator}>•</span>
          <span className={styles.dataCount}>
            {kpis.total.toLocaleString('pt-BR')} eventos carregados
          </span>
        </p>
      </footer>

      <ChatBot
        eventos={eventos}
        kpis={kpis}
        periodo={selectedPeriod}
        dataSelecionada={selectedDate}
      />
    </div>
  );
}

export default App;