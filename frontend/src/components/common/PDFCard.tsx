import { FileText, Clock, FileCheck } from 'lucide-react';

interface PDFCardProps {
  title: string;
  filename: string;
  fileSize: string;
  totalPages?: number;
  uploadDate?: string;
  isSelected?: boolean;
  onClick?: () => void;
}

export const PDFCard = ({
  title,
  filename,
  fileSize,
  totalPages = 12,
  uploadDate = 'Just now',
  isSelected = false,
  onClick,
}: PDFCardProps) => {
  return (
    <div
      onClick={onClick}
      className={`group relative p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
        isSelected
          ? 'bg-blue-950/40 border-blue-500/60 shadow-lg shadow-blue-950/40 ring-1 ring-blue-500/40'
          : 'bg-slate-900/60 hover:bg-slate-900 border-slate-800/80 hover:border-slate-700'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-lg bg-red-950/60 border border-red-800/50 flex items-center justify-center text-red-400 shrink-0 group-hover:scale-105 transition-transform">
          <FileText className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium text-slate-100 truncate group-hover:text-blue-300 transition-colors">
            {title}
          </h4>
          <p className="text-xs text-slate-400 truncate mt-0.5">{filename}</p>
          <div className="flex items-center gap-3 text-xs text-slate-500 mt-2">
            <span className="flex items-center gap-1">
              <FileCheck className="w-3.5 h-3.5 text-blue-400" />
              {totalPages} pages
            </span>
            <span>•</span>
            <span>{fileSize}</span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {uploadDate}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
