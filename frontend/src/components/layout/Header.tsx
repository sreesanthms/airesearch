import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BookOpenText, Info, Sparkles, Upload } from 'lucide-react';
import { Button, Modal } from '../common';

export const Header = () => {
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const location = useLocation();
  const isChatPage = location.pathname.startsWith('/chat');

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Brand Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-600/20 group-hover:scale-105 transition-transform">
                <BookOpenText className="w-5 h-5" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                  ResearchPilot
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-blue-950 text-blue-400 border border-blue-800/50">
                    v1.0
                  </span>
                </span>
              </div>
            </Link>

            {/* Right Nav */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsAboutOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-lg transition-colors"
              >
                <Info className="w-4 h-4 text-blue-400" />
                <span>About</span>
              </button>

              {isChatPage && (
                <Link to="/">
                  <Button variant="secondary" size="sm" leftIcon={<Upload className="w-3.5 h-3.5" />}>
                    Upload New
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* About Modal */}
      <Modal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} title="About ResearchPilot">
        <div className="space-y-4 text-slate-300 text-sm leading-relaxed">
          <div className="flex items-center gap-3 p-3 rounded-xl bg-blue-950/40 border border-blue-800/50 text-blue-300">
            <Sparkles className="w-5 h-5 shrink-0" />
            <p className="text-xs">
              Powered by Retrieval-Augmented Generation (RAG) using PyMuPDF, Sentence Transformers, FAISS & Google Gemini.
            </p>
          </div>

          <p>
            <strong>ResearchPilot</strong> is a production-quality AI application designed to help researchers, students, and academics rapidly extract insights from academic PDFs.
          </p>

          <div className="space-y-2">
            <h4 className="font-semibold text-slate-100">Key Capabilities:</h4>
            <ul className="list-disc list-inside space-y-1 text-slate-400 text-xs">
              <li>Instant executive paper summaries & section breakdowns</li>
              <li>Methodology deep-dives & equation explanations</li>
              <li>Automated viva examination question generator</li>
              <li>Exact page-numbered source chunk citations</li>
            </ul>
          </div>

          <div className="pt-2 flex justify-end">
            <Button variant="primary" size="sm" onClick={() => setIsAboutOpen(false)}>
              Got it
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
};
