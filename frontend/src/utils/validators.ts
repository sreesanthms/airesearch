import { MAX_FILE_SIZE, ACCEPTED_FILE_TYPES } from './constants';

export const validatePdfFile = (file: File): { valid: boolean; error?: string } => {
  if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
    return { valid: false, error: 'Please upload a valid PDF file.' };
  }
  
  if (file.size > MAX_FILE_SIZE) {
    return { valid: false, error: 'File size exceeds the 10MB limit.' };
  }
  
  return { valid: true };
};
