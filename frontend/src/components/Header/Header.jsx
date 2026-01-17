import { Shield, Activity } from 'lucide-react';
import styles from './Header.module.css';

export function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.logoSection}>
          <div className={styles.iconWrapper}>
            <Shield size={28} strokeWidth={1.5} />
          </div>
          <div className={styles.titleGroup}>
            <h1 className={styles.title}>
              Monitoramento de Risco Operacional
            </h1>
            <p className={styles.subtitle}>
              Sistema de análise com IA · <span className={styles.brand}>Yoyo</span> 💜
            </p>
          </div>
        </div>

        <div className={styles.statusIndicator}>
          <Activity size={16} className={styles.pulseIcon} />
          <span>Sistema Ativo</span>
        </div>
      </div>
    </header>
  );
}
