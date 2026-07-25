import { CheckCircle2, FileText, Loader2 } from 'lucide-react';

interface UploadProgressProps {
  filename: string;
  progress: number;
  statusText?: string;
  onCancel?: () => void;
}

export const UploadProgress = ({
  filename,
  progress,
  statusText = 'Processing paper with RAG...',
}: UploadProgressProps) => {
  return (
    <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-xl animate-fadeIn">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-xl bg-blue-950 border border-blue-800/60 flex items-center justify-center text-blue-400 shrink-0">
          <FileText className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-200 truncate">{filename}</h4>
            <span className="text-xs font-mono text-blue-400">{progress}%</span>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
            {progress < 100 ? (
              <Loader2 className="w-3 h-3 animate-spin text-blue-400" />
            ) : (
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            )}
            {statusText}
          </p>
        </div>
      </div>

      <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800/80">
        <div
          className="bg-gradient-to-r from-blue-600 to-indigo-500 h-full transition-all duration-300 rounded-full"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};
