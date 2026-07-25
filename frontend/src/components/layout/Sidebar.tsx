import { useState } from 'react';
import {
  FileText,
  Zap,
  Microscope,
  HelpCircle,
  Rocket,
  Plus,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Layers,
} from 'lucide-react';
import { Link } from 'react-router-dom';

interface SidebarProps {
  paperTitle?: string;
  filename?: string;
  fileSize?: string;
  totalPages?: number;
  onPresetClick?: (promptText: string) => void;
  isMobileOpen?: boolean;
  onMobileClose?: () => void;
}

export const Sidebar = ({
  paperTitle = 'Attention Is All You Need',
  filename = 'attention_is_all_you_need.pdf',
  fileSize = '2.4 MB',
  totalPages = 15,
  onPresetClick,
  isMobileOpen = false,
  onMobileClose,
}: SidebarProps) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const presets = [
    {
      id: 'summary',
      label: 'Summary',
      icon: <Zap className="w-4 h-4 text-amber-400" />,
      prompt: 'Provide a comprehensive summary of this research paper including key findings.',
    },
    {
      id: 'methodology',
      label: 'Methodology',
      icon: <Microscope className="w-4 h-4 text-blue-400" />,
      prompt: 'Explain the core methodology, architecture, and mathematical formulation used in this paper.',
    },
    {
      id: 'viva',
      label: 'Viva Questions',
      icon: <HelpCircle className="w-4 h-4 text-indigo-400" />,
      prompt: 'Generate 5 challenging viva exam questions based on this paper along with model answers.',
    },
    {
      id: 'future',
      label: 'Future Work',
      icon: <Rocket className="w-4 h-4 text-emerald-400" />,
      prompt: 'Summarize the limitations mentioned by the authors and proposed future research directions.',
    },
  ];

  const recentPapers = [
    { id: 'paper-attention-2026', title: 'Attention Is All You Need', size: '2.4 MB', pages: 15 },
    { id: 'paper-gemini-flash-2026', title: 'Gemini: High Efficiency Multimodal Models', size: '4.1 MB', pages: 32 },
    { id: 'paper-rag-survey-2026', title: 'Retrieval-Augmented Generation Survey', size: '1.8 MB', pages: 12 },
  ];

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isMobileOpen && (
        <div
          onClick={onMobileClose}
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm md:hidden"
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 flex flex-col bg-slate-900 border-r border-slate-800 transition-all duration-300 ${
          isCollapsed ? 'w-20' : 'w-72'
        } ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Toggle Collapse Button (Desktop) */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="hidden md:flex absolute -right-3 top-20 w-6 h-6 rounded-full bg-slate-800 border border-slate-700 text-slate-400 hover:text-white items-center justify-center shadow-lg transition-transform"
          aria-label="Toggle sidebar"
        >
          {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
        </button>

        {/* Top Upload Action */}
        <div className="p-4 border-b border-slate-800/80">
          <Link
            to="/"
            className={`flex items-center justify-center gap-2 w-full p-2.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/40 text-blue-300 font-medium text-sm transition-all ${
              isCollapsed ? 'px-0' : ''
            }`}
          >
            <Plus className="w-4 h-4 shrink-0" />
            {!isCollapsed && <span>Upload New PDF</span>}
          </Link>
        </div>

        {/* Active PDF Information Card */}
        {!isCollapsed && (
          <div className="p-4 border-b border-slate-800/80 bg-slate-950/40">
            <div className="flex items-center gap-2 text-xs font-semibold text-blue-400 uppercase tracking-wider mb-2">
              <Sparkles className="w-3.5 h-3.5" /> Active Document
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
              <div className="flex items-start gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-red-950/80 border border-red-800/60 flex items-center justify-center text-red-400 shrink-0">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="text-xs font-semibold text-slate-100 truncate">{paperTitle}</h4>
                  <p className="text-[11px] text-slate-400 truncate mt-0.5">{filename}</p>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/60 font-mono">
                <span>{totalPages} Pages</span>
                <span>{fileSize}</span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Indexed
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Quick Action Presets */}
        <div className="p-4 border-b border-slate-800/80">
          {!isCollapsed && (
            <h3 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Quick AI Presets
            </h3>
          )}
          <div className="space-y-1.5">
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => onPresetClick && onPresetClick(preset.prompt)}
                title={isCollapsed ? preset.label : undefined}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-slate-800/80 transition-colors text-left ${
                  isCollapsed ? 'justify-center px-0' : ''
                }`}
              >
                {preset.icon}
                {!isCollapsed && <span>{preset.label}</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Recent Papers */}
        <div className="flex-1 overflow-y-auto p-4">
          {!isCollapsed && (
            <h3 className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center justify-between">
              <span>Recent Papers</span>
              <Layers className="w-3.5 h-3.5 text-slate-500" />
            </h3>
          )}
          <div className="space-y-1.5">
            {recentPapers.map((paper) => (
              <Link
                key={paper.id}
                to={`/chat/${paper.id}`}
                title={isCollapsed ? paper.title : undefined}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 transition-colors truncate ${
                  isCollapsed ? 'justify-center px-0' : ''
                }`}
              >
                <FileText className="w-4 h-4 text-slate-500 shrink-0" />
                {!isCollapsed && <span className="truncate">{paper.title}</span>}
              </Link>
            ))}
          </div>
        </div>
      </aside>
    </>
  );
};
