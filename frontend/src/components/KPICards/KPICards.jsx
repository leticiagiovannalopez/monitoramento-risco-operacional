import {
  BarChart3,
  AlertTriangle,
  AlertCircle,
  AlertOctagon,
  CheckCircle2
} from 'lucide-react';
import styles from './KPICards.module.css';

const cardConfig = [
  {
    id: 'total',
    key: 'total',
    label: 'Total de Eventos',
    icon: BarChart3,
    variant: 'primary',
  },
  {
    id: 'critico',
    key: 'critico',
    label: 'Críticos',
    icon: AlertOctagon,
    variant: 'critical',
    emoji: '🔴'
  },
  {
    id: 'alto',
    key: 'alto',
    label: 'Altos',
    icon: AlertTriangle,
    variant: 'high',
    emoji: '🟠'
  },
  {
    id: 'medio',
    key: 'medio',
    label: 'Médios',
    icon: AlertCircle,
    variant: 'medium',
    emoji: '🟡'
  },
  {
    id: 'baixo',
    key: 'baixo',
    label: 'Baixos',
    icon: CheckCircle2,
    variant: 'low',
    emoji: '🟢'
  }
];

function formatNumber(num) {
  return new Intl.NumberFormat('pt-BR').format(num);
}

export function KPICards({ data }) {
  return (
    <section className={styles.section}>
      <div className={styles.grid}>
        {cardConfig.map((card, index) => {
          const Icon = card.icon;
          const value = data[card.key];
          return (
            <article
              key={card.id}
              className={`${styles.card} ${styles[card.variant]}`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={styles.cardHeader}>
                <div className={styles.iconWrapper}>
                  <Icon size={22} strokeWidth={1.5} />
                </div>
                {card.emoji && <span className={styles.emoji}>{card.emoji}</span>}
              </div>

              <div className={styles.cardContent}>
                <span className={styles.value}>{formatNumber(value)}</span>
                <span className={styles.label}>{card.label}</span>
              </div>

              <div className={styles.cardGlow} />
            </article>
          );
        })}
      </div>
    </section>
  );
}
