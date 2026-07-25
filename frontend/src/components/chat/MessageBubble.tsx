import { useState } from 'react';
import { Bot, User, Copy, Check, BookOpen } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';
import type { MessageRole } from '../../types';

export interface SourceCitation {
  pageNumber: number;
  snippet: string;
  score: number;
}

export interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  timestamp?: string;
  sources?: SourceCitation[];
  isStreaming?: boolean;
}

export const MessageBubble = ({
  role,
  content,
  timestamp,
  sources,
  isStreaming = false,
}: MessageBubbleProps) => {
  const [copied, setCopied] = useState(false);
  const isUser = role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`flex items-start gap-3 my-4 animate-fadeIn ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-md ${
          isUser
            ? 'bg-gradient-to-tr from-blue-600 to-indigo-600 text-white'
            : 'bg-slate-900 border border-slate-800 text-blue-400'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Bubble Container */}
      <div className={`flex flex-col max-w-[88%] sm:max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`relative px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none shadow-lg shadow-blue-600/10'
              : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
          }`}
        >
          {isUser ? (
            <div className="whitespace-pre-wrap font-sans text-slate-100">{content}</div>
          ) : (
            <div>
              <MarkdownRenderer content={content} />
              {isStreaming && <span className="animate-blink text-blue-400 font-bold ml-1">|</span>}
            </div>
          )}

          {/* Source Citations Badges */}
          {!isUser && sources && sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-slate-800/80">
              <div className="flex items-center gap-1.5 text-xs text-blue-400 font-medium mb-2">
                <BookOpen className="w-3.5 h-3.5" /> Cited Sources:
              </div>
              <div className="flex flex-wrap gap-2">
                {sources.map((src, idx) => (
                  <span
                    key={idx}
                    title={src.snippet}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-950/60 border border-blue-800/40 text-[11px] font-mono text-blue-300 hover:bg-blue-900/40 transition-colors cursor-pointer"
                  >
                    <span>Page {src.pageNumber}</span>
                    <span className="text-blue-500">({Math.round(src.score * 100)}% match)</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Bubble Meta Footer */}
        <div className="flex items-center gap-2 mt-1 px-1 text-[11px] text-slate-500">
          {timestamp && <span>{timestamp}</span>}
          {!isUser && (
            <button
              onClick={handleCopy}
              className="hover:text-slate-300 transition-colors flex items-center gap-1"
              aria-label="Copy response"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
