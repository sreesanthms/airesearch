import { AlertCircle, X } from 'lucide-react';

interface ErrorMessageProps {
  title?: string;
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorMessage = ({
  title = 'An error occurred',
  message,
  onDismiss,
  className = '',
}: ErrorMessageProps) => {
  return (
    <div className={`flex items-start gap-3 p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-200 animate-fadeIn ${className}`}>
      <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
      <div className="flex-1 text-sm">
        <h4 className="font-semibold text-red-300">{title}</h4>
        <p className="text-red-300/80 mt-0.5">{message}</p>
      </div>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-200 p-1 rounded-lg hover:bg-red-900/40 transition-colors"
          aria-label="Dismiss error"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
