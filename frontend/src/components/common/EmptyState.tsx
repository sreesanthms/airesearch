import { ReactNode } from 'react';
import { FileSearch } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
}: EmptyStateProps) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center bg-slate-900/40 border border-slate-800/60 rounded-2xl ${className}`}>
      <div className="w-14 h-14 rounded-2xl bg-blue-950/50 border border-blue-800/40 flex items-center justify-center text-blue-400 mb-4 shadow-inner">
        {icon || <FileSearch className="w-7 h-7" />}
      </div>
      <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
      <p className="text-sm text-slate-400 max-w-sm mt-1 mb-6 leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction} size="sm">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
