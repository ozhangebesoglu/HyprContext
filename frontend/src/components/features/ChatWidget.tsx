/**
 * Chat Widget Component
 * ---------------------
 * AI sohbet arayüzü.
 */

import { useState, useRef, useEffect } from 'react';
import { GlassCard } from '../glass/GlassCard';
import { GlassButton } from '../ui/glass-button';
import { GlassInput } from '../ui/glass-input';
import { useChat } from '../../hooks/useApi';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { clsx } from 'clsx';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chat = useChat();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || chat.isPending) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await chat.mutateAsync({
        message: userMessage,
        include_memory: true,
      });
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.response },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Bir hata oluştu. Lütfen tekrar deneyin.' },
      ]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <GlassCard className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
          <Bot size={20} className="text-accent" />
          AI Asistan
        </h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center text-muted">
              <Bot size={48} className="mx-auto mb-4 opacity-50" />
              <p>Merhaba! Size nasıl yardımcı olabilirim?</p>
              <p className="text-sm mt-1">
                Aktiviteleriniz hakkında sorular sorabilirsiniz.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))
        )}
        
        {chat.isPending && (
          <div className="flex items-center gap-2 text-muted">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Düşünüyor...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-3 items-end">
          <GlassInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mesajınızı yazın..."
            disabled={chat.isPending}
          />
          <GlassButton
            onClick={handleSend}
            disabled={!input.trim() || chat.isPending}
            size="icon"
          >
            <Send size={18} />
          </GlassButton>
        </div>
      </div>
    </GlassCard>
  );
}

function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === 'user';

  return (
    <div
      className={clsx(
        'flex gap-3',
        isUser && 'flex-row-reverse'
      )}
    >
      <div
        className={clsx(
          'p-2 rounded-full',
          isUser ? 'bg-accent' : 'bg-white/20'
        )}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-accent" />
        )}
      </div>
      
      <div
        className={clsx(
          'flex-1 p-3 rounded-xl max-w-[80%]',
          isUser ? 'bg-accent text-white' : 'bg-white/10 text-primary'
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
      </div>
    </div>
  );
}
