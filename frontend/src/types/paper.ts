export type PaperStatus = 'uploading' | 'processing' | 'processed' | 'error';

export interface PDFMetadata {
  title?: string | null;
  author?: string | null;
  subject?: string | null;
  creator?: string | null;
  producer?: string | null;
}

export interface Paper {
  id: string;
  title: string;
  filename: string;
  uploadDate: string;
  status: PaperStatus;
  pages?: number;
  wordCount?: number;
  metadata?: PDFMetadata;
}

export interface PaperUploadResponse {
  success: boolean;
  file_name: string;
  pages: number;
  word_count: number;
  character_count: number;
  metadata: PDFMetadata;
  preview: string;
}
