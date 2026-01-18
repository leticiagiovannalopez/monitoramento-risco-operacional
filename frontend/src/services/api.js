import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export async function fetchEventos(filters = {}) {
  try {
    const params = {};
    
    if (filters.data_inicio) {
      params.data_inicio = filters.data_inicio;
    }
    if (filters.data_fim) {
      params.data_fim = filters.data_fim;
    }
    if (filters.nivel_risco) {
      params.nivel_risco = filters.nivel_risco;
    }

    const response = await api.get('/api/eventos', { params });
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar eventos:', error);
    throw new Error('Falha ao buscar eventos. Verifique se o backend está rodando.');
  }
}

export async function fetchEventoById(eventoId) {
  try {
    const response = await api.get(`/api/eventos/${eventoId}`);
    return response.data;
  } catch (error) {
    console.error('Erro ao buscar evento:', error);
    throw new Error('Falha ao buscar detalhes do evento.');
  }
}

export async function sendChatMessage(mensagem, contexto_tela = null, historico = null, nome_usuario = null) {
  try {
    const response = await api.post('/api/yoyo/chat', {
      mensagem,
      contexto_tela,
      historico,
      nome_usuario
    }, {
      timeout: 30000
    });
    return response.data;
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
    throw new Error('Falha ao processar mensagem. Tente novamente.');
  }
}

export async function checkBackendHealth() {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Backend não está respondendo:', error);
    return { status: 'error', timestamp: new Date().toISOString() };
  }
}

export default api;