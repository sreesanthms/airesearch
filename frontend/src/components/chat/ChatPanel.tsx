import { useRef, useEffect } from 'react';
import { MessageBubble, SourceCitation } from './MessageBubble';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from '../common';
import { BookOpenText } from 'lucide-react';
import type { Message } from '../../types';

interface MessageWithSources extends Message {
  sources?: SourceCitation[];
}

interface ChatPanelProps {
  messages: MessageWithSources[];
  isLoading?: boolean;
  isStreaming?: boolean;
  onSendMessage: (text: string) => void;
  paperTitle?: string;
}

export const ChatPanel = ({
  messages,
  isLoading = false,
  isStreaming = false,
  onSendMessage,
  paperTitle = 'Attention Is All You Need',
}: ChatPanelProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: isStreaming ? 'auto' : 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, isStreaming]);

  return (
    <div className="flex flex-col h-full bg-slate-950">
      {/* Scrollable Message List */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400 mb-6 shadow-xl animate-pulse">
              <BookOpenText className="w-8 h-8" />
            </div>
            <h2 className="text-xl font-bold text-slate-100 text-center mb-2">
              Ready to explore <span className="text-blue-400">{paperTitle}</span>
            </h2>
            <p className="text-sm text-slate-400 text-center max-w-md mb-8 leading-relaxed">
              Ask any question about the methodology, results, equations, or future work outlined in this paper.
            </p>

            {/* Quick Starter Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-xl w-full">
              <button
                onClick={() => onSendMessage('Provide a concise executive summary of this paper.')}
                className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800/80 border border-slate-800 text-left transition-all hover:border-blue-500/40 group"
              >
                <span className="text-xs font-semibold text-amber-400 flex items-center gap-1.5 mb-1">
                  ⚡ Executive Summary
                </span>
                <p className="text-xs text-slate-400 group-hover:text-slate-300">
                  Summarize the main problem, hypothesis, and core outcome.
                </p>
              </button>

              <button
                onClick={() => onSendMessage('Explain the key methodology and architecture.')}
                className="p-4 rounded-xl bg-slate-900 hover:bg-slate-800/80 border border-slate-800 text-left transition-all hover:border-blue-500/40 group"
              >
                <span className="text-xs font-semibold text-blue-400 flex items-center gap-1.5 mb-1">
                  🔬 Methodology Breakdown
                </span>
                <p className="text-xs text-slate-400 group-hover:text-slate-300">
                  Deep-dive into the technical approach and neural architecture.
                </p>
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble
              key={msg.id || index}
              role={msg.role}
              content={msg.content}
              timestamp={msg.timestamp}
              sources={msg.sources}
              isStreaming={isStreaming && index === messages.length - 1 && msg.role === 'assistant'}
            />
          ))
        )}

        {isLoading && !isStreaming && (
          <div className="my-4">
            <TypingIndicator label="Searching vectors in FAISS index & asking Gemini..." />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Dock */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/90 backdrop-blur-md">
        <ChatInput onSend={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};
