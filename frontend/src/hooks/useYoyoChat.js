import { useState, useCallback, useRef } from 'react';
import { sendChatMessage } from '../services/api';

export function useYoyoChat() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nomeUsuario, setNomeUsuario] = useState(null);
  const [aguardandoNome, setAguardandoNome] = useState(false);
  const historicoRef = useRef([]);

  const sendMessage = useCallback(async (mensagem, contextoTela = null) => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(
        mensagem,
        contextoTela,
        historicoRef.current,
        nomeUsuario
      );

      historicoRef.current = [
        ...historicoRef.current,
        { role: 'user', content: mensagem },
        { role: 'assistant', content: response.resposta }
      ];

      if (response.aguardando_nome) {
        setAguardandoNome(true);
      }

      if (response.nome_usuario) {
        setNomeUsuario(response.nome_usuario);
        setAguardandoNome(false);
      }

      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [nomeUsuario]);

  const limparConversa = useCallback(() => {
    historicoRef.current = [];
    setNomeUsuario(null);
    setAguardandoNome(false);
  }, []);

  return {
    sendMessage,
    loading,
    error,
    nomeUsuario,
    aguardandoNome,
    limparConversa
  };
}
