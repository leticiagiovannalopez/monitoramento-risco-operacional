import { Clock, Users, DollarSign } from 'lucide-react';
import { riskColors } from '../../data/mockData';
import styles from './EventsTable.module.css';

function RiskBadge({ level }) {
  const normalizedLevel = level?.charAt(0).toUpperCase() + level?.slice(1).toLowerCase();
  const colors = riskColors[normalizedLevel] || riskColors['Médio'];
  return (
    <span
      className={styles.badge}
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
        color: colors.text
      }}
    >
      {normalizedLevel}
    </span>
  );
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatCurrency(value) {
  if (!value && value !== 0) return 'N/A';
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
}

export function EventsTable({ eventos = [], selectedDate = '' }) {
  const filteredEventos = selectedDate
    ? eventos.filter(e => {
        if (!e.data_evento) return false;
        const eventoDate = String(e.data_evento).split('T')[0];
        return eventoDate === selectedDate;
      })
    : eventos;

  const displayEventos = filteredEventos.slice(0, 10);

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.titleGroup}>
          <Clock size={20} className={styles.headerIcon} />
          <h3 className={styles.title}>Eventos Recentes</h3>
        </div>
        <span className={styles.subtitle}>
          {selectedDate ? `Eventos de ${selectedDate}` : `Últimos ${displayEventos.length} eventos registrados`}
        </span>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Data/Hora</th>
              <th>Nível</th>
              <th>Descrição</th>
              <th>
                <span className={styles.thIcon}>
                  <DollarSign size={14} />
                  Impacto Financeiro
                </span>
              </th>
              <th>
                <span className={styles.thIcon}>
                  <Users size={14} />
                  Clientes
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            {displayEventos.length === 0 ? (
              <tr>
                <td colSpan={5} className={styles.emptyMessage}>
                  Nenhum evento encontrado
                </td>
              </tr>
            ) : (
              displayEventos.map((event, index) => (
                <tr
                  key={event.evento_id}
                  className={styles.row}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <td className={styles.dateCell}>{formatDate(event.data_evento)}</td>
                  <td>
                    <RiskBadge level={event.nivel_risco} />
                  </td>
                  <td className={styles.eventType}>{event.descricao}</td>
                  <td className={styles.financial}>{formatCurrency(event.impacto_financeiro)}</td>
                  <td className={styles.clients}>
                    <span className={styles.clientCount}>{event.clientes_afetados?.toLocaleString('pt-BR') || 0}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
