import { useState, KeyboardEvent, useRef, useEffect } from 'react';
import { Sparkles, Paperclip, ArrowUp } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export const ChatInput = ({
  onSend,
  isLoading = false,
  placeholder = 'Ask anything about this paper...',
}: ChatInputProps) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const quickPrompts = [
    'What is the core contribution of this paper?',
    'Explain the key formulas in Section 3.',
    'What datasets were used for evaluation?',
  ];

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Quick Starter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-2 no-scrollbar">
        <span className="text-[11px] font-medium text-slate-500 shrink-0 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-blue-400" /> Suggestions:
        </span>
        {quickPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => onSend(prompt)}
            disabled={isLoading}
            className="shrink-0 px-3 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Box */}
      <div className="relative flex items-end gap-2 p-2 rounded-2xl bg-slate-900 border border-slate-800 focus-within:border-blue-500/60 focus-within:ring-2 focus-within:ring-blue-500/20 shadow-xl transition-all">
        <button
          type="button"
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-xl transition-colors shrink-0 mb-0.5"
          title="Attach additional context file"
        >
          <Paperclip className="w-5 h-5" />
        </button>

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none resize-none py-2 px-1 max-h-40 leading-relaxed"
        />

        <button
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          className={`p-2.5 rounded-xl transition-all shrink-0 mb-0.5 ${
            input.trim() && !isLoading
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-lg shadow-blue-600/30 scale-105 active:scale-95'
              : 'bg-slate-800 text-slate-500 cursor-not-allowed'
          }`}
          aria-label="Send message"
        >
          <ArrowUp className="w-4 h-4" />
        </button>
      </div>

      <p className="text-[11px] text-center text-slate-500 mt-2">
        ResearchPilot uses RAG to ground answers in your uploaded PDF. Verify key equations & citations.
      </p>
    </div>
  );
};
