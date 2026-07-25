import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, FileUp, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { UploadProgress } from './UploadProgress';
import { paperService } from '../../services/paperService';
import { ErrorMessage } from '../common';

interface FileUploaderProps {
  onFileSelect?: (file: File) => void;
}

export const FileUploader = ({ onFileSelect }: FileUploaderProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Uploading PDF...');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const processFile = async (file: File) => {
    setErrorMessage(null);

    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setErrorMessage('Please select a valid PDF research paper.');
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setErrorMessage('File size exceeds the 25MB limit.');
      return;
    }

    setSelectedFile(file);
    setIsUploading(true);
    setUploadProgress(10);
    setStatusMessage('Uploading PDF to backend server...');

    if (onFileSelect) onFileSelect(file);

    try {
      const response = await paperService.uploadPaper(file, (percent) => {
        setUploadProgress(Math.min(percent, 90));
        if (percent > 50) {
          setStatusMessage('Processing text extraction & FAISS vector indexing...');
        }
      });

      // Save upload response details in localStorage for ChatPage
      localStorage.setItem(
        'latest_paper_meta',
        JSON.stringify({
          id: response.file_name,
          title: response.metadata?.title || file.name.replace(/\.pdf$/i, '').replace(/_/g, ' '),
          filename: file.name,
          pages: response.pages,
          wordCount: response.word_count,
          size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        })
      );

      setUploadProgress(100);
      setStatusMessage('Document ready! Opening pilot session...');

      setTimeout(() => {
        navigate(`/chat/${response.file_name}`);
      }, 600);
    } catch (err: unknown) {
      setIsUploading(false);
      setSelectedFile(null);
      const detail =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      setErrorMessage(detail || 'Upload failed. Ensure backend server is running on http://localhost:8000');
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const triggerFileBrowser = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full space-y-4">
      {errorMessage && (
        <ErrorMessage
          title="Upload Error"
          message={errorMessage}
          onDismiss={() => setErrorMessage(null)}
        />
      )}

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileInputChange}
        accept=".pdf,application/pdf"
        className="hidden"
      />

      {isUploading && selectedFile ? (
        <UploadProgress
          filename={selectedFile.name}
          progress={uploadProgress}
          statusText={statusMessage}
        />
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerFileBrowser}
          className={`relative group rounded-2xl border-2 border-dashed transition-all duration-300 p-8 sm:p-12 text-center cursor-pointer overflow-hidden ${
            isDragging
              ? 'border-blue-500 bg-blue-950/30 scale-[1.01] shadow-2xl shadow-blue-500/10'
              : 'border-slate-800 hover:border-blue-500/60 bg-slate-900/50 hover:bg-slate-900/80 shadow-xl'
          }`}
        >
          {/* Subtle glowing radial background */}
          <div className="absolute inset-0 bg-gradient-to-b from-blue-600/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

          <div className="relative z-10 flex flex-col items-center justify-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-b from-slate-800 to-slate-900 border border-slate-700/80 flex items-center justify-center text-blue-400 mb-5 group-hover:scale-110 group-hover:border-blue-500/50 group-hover:text-blue-300 transition-all shadow-lg">
              <Upload className="w-8 h-8" />
            </div>

            <h3 className="text-lg font-semibold text-slate-100 mb-2 flex items-center gap-2">
              <span>Drop your research paper PDF here</span>
              <Sparkles className="w-4 h-4 text-blue-400 opacity-80" />
            </h3>

            <p className="text-sm text-slate-400 max-w-sm mb-6 leading-relaxed">
              Drag & drop a paper file or <span className="text-blue-400 underline underline-offset-4 font-medium">browse your device</span>.
            </p>

            <div className="flex items-center gap-4 px-4 py-2 rounded-full bg-slate-950/80 border border-slate-800 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <FileUp className="w-3.5 h-3.5 text-blue-400" /> PDF format
              </span>
              <span>•</span>
              <span>Max file size: 25MB</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
