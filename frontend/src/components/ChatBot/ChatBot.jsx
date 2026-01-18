import { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X, Minimize2, Sparkles, RotateCcw } from 'lucide-react';
import { useYoyoChat } from '../../hooks/useYoyoChat';
import styles from './ChatBot.module.css';

const initialMessages = [
  {
    id: 1,
    type: 'bot',
    text: 'Olá! Sou a Yoyo, sua assistente de análise de risco operacional. Como posso ajudar você hoje?',
    time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }
];

export function ChatBot({ eventos = [], kpis = {}, periodo = '', dataSelecionada = null }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const { sendMessage, loading, limparConversa } = useYoyoChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSend = async () => {
    if (!inputValue.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: inputValue,
      time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    };

    const mensagem = inputValue;
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const contextoTela = {
        eventos: eventos.slice(0, 10),
        kpis,
        periodo,
        data_selecionada: dataSelecionada
      };

      const response = await sendMessage(mensagem, contextoTela);

      const botResponse = {
        id: Date.now() + 1,
        type: 'bot',
        text: response.resposta || 'Desculpe, não consegui processar sua mensagem.',
        time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (err) {
      const errorResponse = {
        id: Date.now() + 1,
        type: 'bot',
        text: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        time: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };

  const minimizeChat = () => {
    setIsMinimized(!isMinimized);
  };

  return (
    <>
      {!isOpen && (
        <button className={styles.floatingButton} onClick={toggleChat}>
          <MessageCircle size={24} />
          <span className={styles.buttonPulse} />
        </button>
      )}

      {isOpen && (
        <div className={`${styles.chatWindow} ${isMinimized ? styles.minimized : ''}`}>
          <div className={styles.chatHeader} onClick={isMinimized ? minimizeChat : undefined}>
            <div className={styles.headerInfo}>
              <div className={styles.avatarWrapper}>
                <img
                  src="/Avatar_yoyo.jpeg"
                  alt="Yoyo AI"
                  className={styles.avatar}
                />
                <span className={styles.onlineIndicator} />
              </div>
              <div className={styles.headerText}>
                <h4 className={styles.botName}>Yoyo</h4>
                <span className={styles.botStatus}>
                  <Sparkles size={12} />
                  Assistente IA
                </span>
              </div>
            </div>
            <div className={styles.headerActions}>
              <button className={styles.headerButton} onClick={() => { limparConversa(); setMessages(initialMessages); }} title="Nova conversa">
                <RotateCcw size={18} />
              </button>
              <button className={styles.headerButton} onClick={minimizeChat}>
                <Minimize2 size={18} />
              </button>
              <button className={styles.headerButton} onClick={toggleChat}>
                <X size={18} />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              <div className={styles.messagesContainer}>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`${styles.message} ${styles[message.type]}`}
                  >
                    {message.type === 'bot' && (
                      <img
                        src="/Avatar_yoyo.jpeg"
                        alt="Yoyo"
                        className={styles.messageAvatar}
                      />
                    )}
                    <div className={styles.messageContent}>
                      <p className={styles.messageText}>{message.text}</p>
                      <span className={styles.messageTime}>{message.time}</span>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className={`${styles.message} ${styles.bot}`}>
                    <img
                      src="/Avatar_yoyo.jpeg"
                      alt="Yoyo"
                      className={styles.messageAvatar}
                    />
                    <div className={styles.typingIndicator}>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <div className={styles.inputContainer}>
                <input
                  ref={inputRef}
                  type="text"
                  className={styles.input}
                  placeholder="Digite sua mensagem..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
                <button
                  className={styles.sendButton}
                  onClick={handleSend}
                  disabled={!inputValue.trim()}
                >
                  <Send size={18} />
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
