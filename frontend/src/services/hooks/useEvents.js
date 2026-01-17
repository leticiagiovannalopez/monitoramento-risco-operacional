import { useState, useEffect, useCallback } from 'react';
import { fetchEventos } from '../services/api';

export function useEvents(filters = {}) {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  const [kpis, setKpis] = useState({
    total: 0,
    critico: 0,
    alto: 0,
    medio: 0,
    baixo: 0
  });

  const calculateKPIs = useCallback((eventosData) => {
    const stats = {
      total: eventosData.length,
      critico: eventosData.filter(e => e.nivel_risco === 'critico').length,
      alto: eventosData.filter(e => e.nivel_risco === 'alto').length,
      medio: eventosData.filter(e => e.nivel_risco === 'medio').length,
      baixo: eventosData.filter(e => e.nivel_risco === 'baixo').length
    };
    setKpis(stats);
    return stats;
  }, []);

  const loadEventos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await fetchEventos(filters);
      
      setEventos(data.eventos || []);
      setTotal(data.total || 0);
      calculateKPIs(data.eventos || []);

      } catch (err) {
      setError(err.message);
      console.error('Erro ao carregar eventos:', err);
    } finally {
      setLoading(false);
    }
  }, [filters, calculateKPIs]);

  useEffect(() => {
    loadEventos();
  }, [loadEventos]);

  const refetch = useCallback(() => {
    loadEventos();
  }, [loadEventos]);

  return {
    eventos,
    loading,
    error,
    total,
    kpis,
    refetch
  };
}
