interface TypingIndicatorProps {
  label?: string;
}

export const TypingIndicator = ({ label = 'ResearchPilot is thinking...' }: TypingIndicatorProps) => {
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-slate-900/90 border border-slate-800/80 text-slate-300 w-fit animate-fadeIn">
      <div className="flex items-center gap-1">
        <span className="typing-dot bg-blue-400"></span>
        <span className="typing-dot bg-blue-400"></span>
        <span className="typing-dot bg-blue-400"></span>
      </div>
      {label && <span className="text-xs text-slate-400 font-medium tracking-wide">{label}</span>}
    </div>
  );
};
