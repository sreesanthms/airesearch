import { api } from './api';
import { Paper, PaperUploadResponse } from '../types/paper';

export const paperService = {
  uploadPaper: async (
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<PaperUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<PaperUploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percent);
        }
      },
    });

    return response.data;
  },

  getPaper: async (paperId: string): Promise<Paper> => {
    return {
      id: paperId,
      title: paperId.replace(/\.pdf$/i, '').replace(/_/g, ' '),
      filename: paperId,
      uploadDate: new Date().toISOString(),
      status: 'processed',
    };
  },

  listPapers: async (): Promise<Paper[]> => {
    return [];
  },
};
