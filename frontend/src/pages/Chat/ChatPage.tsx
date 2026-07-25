import { useState, useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Sidebar } from '../../components/layout';
import { ChatPanel } from '../../components/chat';
import { Button } from '../../components/common';
import { FileText, Menu, Share2, Upload } from 'lucide-react';
import { chatService } from '../../services/chatService';
import type { Message } from '../../types';
import type { SourceCitation } from '../../components/chat/MessageBubble';

interface MessageWithSources extends Message {
  sources?: SourceCitation[];
}

export const ChatPage = () => {
  const { paperId } = useParams<{ paperId: string }>();
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  // Retrieve stored paper metadata if available
  const storedMeta = useMemo(() => {
    try {
      const raw = localStorage.getItem('latest_paper_meta');
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && parsed.id === paperId) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse paper metadata:', e);
    }
    return null;
  }, [paperId]);

  const displayTitle = storedMeta?.title || (paperId ? paperId.replace(/\.pdf$/i, '').replace(/_/g, ' ') : 'Attention Is All You Need');
  const filename = storedMeta?.filename || paperId || 'uploaded_document.pdf';
  const totalPages = storedMeta?.pages || 15;
  const fileSize = storedMeta?.size || 'Indexed Document';

  const [messages, setMessages] = useState<MessageWithSources[]>([]);

  const handleSendMessage = async (text: string) => {
    const userMsg: MessageWithSources = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    const assistantMsgId = crypto.randomUUID();
    let accumulatedContent = '';
    let isFirstToken = true;
    const activePaperId = paperId || 'paper-attention-2026';

    await chatService.streamMessage(
      activePaperId,
      text,
      messages.map((m) => ({ role: m.role, content: m.content, id: m.id, timestamp: m.timestamp })),
      {
        onToken: (token: string) => {
          if (isFirstToken) {
            isFirstToken = false;
            setIsLoading(false);
            setIsStreaming(true);

            accumulatedContent = token;
            const initialAssistantMsg: MessageWithSources = {
              id: assistantMsgId,
              role: 'assistant',
              content: accumulatedContent,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, initialAssistantMsg]);
          } else {
            accumulatedContent += token;
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId ? { ...msg, content: accumulatedContent } : msg
              )
            );
          }
        },
        onDone: () => {
          setIsLoading(false);
          setIsStreaming(false);
        },
        onError: (err: string) => {
          setIsLoading(false);
          setIsStreaming(false);
          const errorMsg: MessageWithSources = {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Error: ${err}`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          };
          setMessages((prev) => [...prev, errorMsg]);
        },
      }
    );
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Header Bar */}
      <header className="h-16 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md flex items-center justify-between px-4 sm:px-6 shrink-0 z-30">
        <div className="flex items-center gap-3">
          {/* Mobile Toggle Button */}
          <button
            onClick={() => setIsMobileSidebarOpen(true)}
            className="md:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-900"
          >
            <Menu className="w-5 h-5" />
          </button>

          <Link to="/" className="hidden sm:flex items-center gap-2 text-slate-400 hover:text-white text-xs transition-colors">
            <span className="font-semibold text-slate-200">ResearchPilot</span>
            <span>/</span>
          </Link>

          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-red-950/80 border border-red-800/60 flex items-center justify-center text-red-400 shrink-0">
              <FileText className="w-4 h-4" />
            </div>
            <h1 className="text-sm font-semibold text-slate-100 truncate max-w-xs sm:max-w-md capitalize">
              {displayTitle}
            </h1>
          </div>

          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-[11px] font-medium text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>RAG Connected</span>
          </div>
        </div>

        {/* Action Header Tools */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => alert('Conversation transcript copied to clipboard!')}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-900 rounded-xl transition-colors text-xs flex items-center gap-1.5"
            title="Export / Share Chat"
          >
            <Share2 className="w-4 h-4" />
            <span className="hidden sm:inline">Share</span>
          </button>

          <Link to="/">
            <Button variant="secondary" size="sm" leftIcon={<Upload className="w-3.5 h-3.5" />}>
              <span className="hidden sm:inline">Upload New</span>
            </Button>
          </Link>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <Sidebar
          paperTitle={displayTitle}
          filename={filename}
          fileSize={fileSize}
          totalPages={totalPages}
          onPresetClick={handleSendMessage}
          isMobileOpen={isMobileSidebarOpen}
          onMobileClose={() => setIsMobileSidebarOpen(false)}
        />

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-w-0 h-full relative">
          <ChatPanel
            messages={messages}
            isLoading={isLoading}
            isStreaming={isStreaming}
            onSendMessage={handleSendMessage}
            paperTitle={displayTitle}
          />
        </main>
      </div>
    </div>
  );
};
