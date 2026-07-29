export const APP_NAME = 'ResearchPilot';

/**
 * Dynamically resolves the API Base URL.
 * Enforces relative path '/api/v1' in production to work seamlessly with Nginx / Elastic Beanstalk.
 */
const getApiBaseUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_BASE_URL?.trim();

  // In production mode (Docker / Elastic Beanstalk build), ALWAYS use relative path /api/v1
  if (import.meta.env.MODE === 'production') {
    if (envUrl && !envUrl.includes('localhost') && !envUrl.includes('127.0.0.1')) {
      return envUrl;
    }
    return '/api/v1';
  }

  // Development mode fallback
  return envUrl || '/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();
export const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB
export const ACCEPTED_FILE_TYPES = ['application/pdf'];
