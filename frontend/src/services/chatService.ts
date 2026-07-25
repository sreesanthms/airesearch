import { API_BASE_URL } from '../utils/constants';
import { Message } from '../types/chat';

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export const chatService = {
  streamMessage: async (
    paperId: string,
    question: string,
    history: Message[],
    callbacks: StreamCallbacks
  ): Promise<void> => {
    try {
      const formattedHistory = history.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'text/event-stream',
        },
        body: JSON.stringify({
          paper_id: paperId,
          question,
          history: formattedHistory,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to connect to chat API.' }));
        callbacks.onError(errorData.detail || `Server returned ${response.status}`);
        return;
      }

      if (!response.body) {
        callbacks.onError('ReadableStream not supported by browser environment.');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith('data: ')) {
            const rawJson = trimmed.slice(6);
            try {
              const data = JSON.parse(rawJson);
              if (data.token) {
                callbacks.onToken(data.token);
              }
              if (data.error) {
                callbacks.onError(data.error);
              }
              if (data.done) {
                callbacks.onDone();
                return;
              }
            } catch (e) {
              console.warn('Failed to parse SSE JSON:', rawJson);
            }
          }
        }
      }

      callbacks.onDone();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Network failure during chat stream.';
      callbacks.onError(msg);
    }
  },

  getHistory: async (_paperId: string): Promise<Message[]> => {
    return [];
  },
};
