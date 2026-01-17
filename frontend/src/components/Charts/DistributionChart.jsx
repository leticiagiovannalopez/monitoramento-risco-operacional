import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { BarChart3 } from 'lucide-react';
import styles from './Charts.module.css';

export function DistributionChart({ data, total }) {
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0];
      const percentage = ((item.value / total) * 100).toFixed(1);
      return (
        <div className={styles.tooltip}>
          <p className={styles.tooltipItem} style={{ color: item.payload.color }}>
            {item.payload.name}: <strong>{item.value.toLocaleString('pt-BR')}</strong>
          </p>
          <p className={styles.tooltipPercentage}>{percentage}% do total</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.titleGroup}>
          <BarChart3 size={20} className={styles.headerIcon} />
          <h3 className={styles.title}>Distribuição por Nível</h3>
        </div>
        <span className={styles.subtitle}>Visão geral</span>
      </div>

      <div className={styles.chartContainer}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 20, right: 30, left: 60, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--color-border)"
              horizontal={true}
              vertical={false}
            />
            <XAxis
              type="number"
              stroke="var(--color-text-muted)"
              tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
              axisLine={{ stroke: 'var(--color-border)' }}
              tickFormatter={(value) => value.toLocaleString('pt-BR')}
            />
            <YAxis
              type="category"
              dataKey="name"
              stroke="var(--color-text-muted)"
              tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
              axisLine={{ stroke: 'var(--color-border)' }}
              width={50}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }} />
            <Bar
              dataKey="value"
              radius={[0, 6, 6, 0]}
              barSize={32}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className={styles.statsRow}>
        {data.map((item) => (
          <div key={item.name} className={styles.statItem}>
            <span className={styles.statDot} style={{ backgroundColor: item.color }} />
            <span className={styles.statLabel}>{item.name}</span>
            <span className={styles.statValue}>{((item.value / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
