import { useState, useCallback, useRef } from 'react';
import { sendChatMessage } from '../services/api';

const ConversationState = {
  INICIO: 'INICIO',
  AGUARDANDO_NOME: 'AGUARDANDO_NOME',
  ATIVO: 'ATIVO'
};

const STORAGE_KEY = 'yoyo_chat_state';

function loadFromStorage() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {}
  return null;
}

function saveToStorage(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (e) {}
}

export function useYoyoChat() {
  const savedState = loadFromStorage();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [nomeUsuario, setNomeUsuario] = useState(savedState?.nomeUsuario || null);
  const [conversationState, setConversationState] = useState(
    savedState?.nomeUsuario ? ConversationState.ATIVO : ConversationState.INICIO
  );
  const historicoRef = useRef([]);

  const sendMessage = useCallback(async (mensagem, contextoTela = null) => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(
        mensagem,
        contextoTela,
        historicoRef.current,
        nomeUsuario,
        conversationState
      );

      historicoRef.current = [
        ...historicoRef.current,
        { role: 'user', content: mensagem },
        { role: 'assistant', content: response.resposta }
      ];

      if (response.conversation_state) {
        setConversationState(response.conversation_state);
      }

      if (response.nome_usuario) {
        setNomeUsuario(response.nome_usuario);
        saveToStorage({ nomeUsuario: response.nome_usuario });
      }

      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [nomeUsuario, conversationState]);

  const iniciarConversa = useCallback(async (contextoTela = null) => {
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(
        '__INICIO__',
        contextoTela,
        [],
        nomeUsuario,
        ConversationState.INICIO
      );

      historicoRef.current = [
        { role: 'assistant', content: response.resposta }
      ];

      if (response.conversation_state) {
        setConversationState(response.conversation_state);
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
    setConversationState(ConversationState.INICIO);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    sendMessage,
    iniciarConversa,
    loading,
    error,
    nomeUsuario,
    conversationState,
    limparConversa
  };
}
