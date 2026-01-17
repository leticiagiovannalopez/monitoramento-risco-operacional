import { Clock, Users, DollarSign, AlertCircle } from 'lucide-react';
import { recentEvents, riskColors } from '../../data/mockData';
import styles from './EventsTable.module.css';

function RiskBadge({ level }) {
  const colors = riskColors[level];
  return (
    <span
      className={styles.badge}
      style={{
        backgroundColor: colors.bg,
        borderColor: colors.border,
        color: colors.text
      }}
    >
      {level}
    </span>
  );
}

export function EventsTable() {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.titleGroup}>
          <Clock size={20} className={styles.headerIcon} />
          <h3 className={styles.title}>Eventos Recentes</h3>
        </div>
        <span className={styles.subtitle}>Últimos 10 eventos registrados</span>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Data/Hora</th>
              <th>Nível</th>
              <th>Tipo de Evento</th>
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
            {recentEvents.map((event, index) => (
              <tr
                key={event.id}
                className={styles.row}
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                <td className={styles.dateCell}>{event.data}</td>
                <td>
                  <RiskBadge level={event.nivel_risco} />
                </td>
                <td className={styles.eventType}>{event.tipo_evento}</td>
                <td className={styles.financial}>{event.impacto_financeiro}</td>
                <td className={styles.clients}>
                  <span className={styles.clientCount}>{event.clientes_afetados}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
