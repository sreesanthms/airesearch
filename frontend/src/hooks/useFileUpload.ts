import { useState } from 'react';
import type { PaperUploadResponse } from '../types';
import { paperService } from '../services/paperService';

interface UseFileUploadReturn {
  file: File | null;
  isUploading: boolean;
  progress: number;
  error: string | null;
  uploadResponse: PaperUploadResponse | null;
  upload: (file: File) => Promise<void>;
  reset: () => void;
}

/**
 * Custom hook for managing file upload state and logic.
 * Handles upload progress, error states, and response data.
 */
export const useFileUpload = (): UseFileUploadReturn => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [uploadResponse, setUploadResponse] = useState<PaperUploadResponse | null>(null);

  const upload = async (_file: File): Promise<void> => {
    setFile(_file);
    setIsUploading(true);
    setProgress(0);
    setError(null);

    try {
      const res = await paperService.uploadPaper(_file, (percent) => setProgress(percent));
      setIsUploading(false);
      setProgress(100);
      setUploadResponse(res);
    } catch (err: unknown) {
      setIsUploading(false);
      const msg = err instanceof Error ? err.message : 'File upload failed.';
      setError(msg);
    }
  };

  const reset = () => {
    setFile(null);
    setIsUploading(false);
    setProgress(0);
    setError(null);
    setUploadResponse(null);
  };

  return { file, isUploading, progress, error, uploadResponse, upload, reset };
};
