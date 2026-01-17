import { useState } from 'react';
import { Calendar, ChevronDown, CalendarDays } from 'lucide-react';
import styles from './DateFilter.module.css';

const periods = [
  { value: '7d', label: 'Últimos 7 dias' },
  { value: '15d', label: 'Últimos 15 dias' },
  { value: '30d', label: 'Últimos 30 dias' },
  { value: '3m', label: 'Últimos 3 meses' },
  { value: '6m', label: 'Últimos 6 meses' },
  { value: '12m', label: 'Últimos 12 meses' },
  { value: 'custom', label: 'Período personalizado' }
];

export function DateFilter({ selectedPeriod, onPeriodChange, selectedDate, onDateChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showCustom, setShowCustom] = useState(false);
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');

  const selectedLabel = periods.find(p => p.value === selectedPeriod)?.label || 'Selecione';

  const handleSelect = (period) => {
    if (period.value === 'custom') {
      setShowCustom(true);
    } else {
      onPeriodChange(period.value);
      setShowCustom(false);
    }
    setIsOpen(false);
  };

  const handleCustomApply = () => {
    if (customStart && customEnd) {
      onPeriodChange(`${customStart}_${customEnd}`);
      setShowCustom(false);
    }
  };

  const handleDateChange = (e) => {
    onDateChange?.(e.target.value);
  };

  const clearDate = () => {
    onDateChange?.('');
  };

  return (
    <div className={styles.container}>
      <div className={styles.filterGroup}>
        <span className={styles.label}>Período:</span>

        <div className={styles.dropdown}>
          <button
            className={styles.trigger}
            onClick={() => setIsOpen(!isOpen)}
          >
            <Calendar size={16} />
            <span>{selectedLabel}</span>
            <ChevronDown size={16} className={`${styles.chevron} ${isOpen ? styles.open : ''}`} />
          </button>

          {isOpen && (
            <div className={styles.menu}>
              {periods.map((period) => (
                <button
                  key={period.value}
                  className={`${styles.menuItem} ${selectedPeriod === period.value ? styles.active : ''}`}
                  onClick={() => handleSelect(period)}
                >
                  {period.label}
                </button>
              ))}
            </div>
          )}
        </div>

        {showCustom && (
          <div className={styles.customRange}>
            <input
              type="date"
              className={styles.dateInput}
              value={customStart}
              onChange={(e) => setCustomStart(e.target.value)}
            />
            <span className={styles.dateSeparator}>até</span>
            <input
              type="date"
              className={styles.dateInput}
              value={customEnd}
              onChange={(e) => setCustomEnd(e.target.value)}
            />
            <button className={styles.applyBtn} onClick={handleCustomApply}>
              Aplicar
            </button>
          </div>
        )}

        <div className={styles.divider} />

        <span className={styles.label}>Dia específico:</span>

        <div className={styles.datePickerWrapper}>
          <CalendarDays size={16} className={styles.datePickerIcon} />
          <input
            type="date"
            className={styles.datePicker}
            value={selectedDate || ''}
            onChange={handleDateChange}
          />
          {selectedDate && (
            <button className={styles.clearBtn} onClick={clearDate}>
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
