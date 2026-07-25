export type MessageRole = 'user' | 'assistant';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  paperId: string;
  question: string;
  history?: Message[];
}

export interface ChatResponse {
  answer: string;
  sources?: string[];
}
