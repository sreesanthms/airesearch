import { useNavigate } from 'react-router-dom';
import { FileUploader } from '../../components/upload';
import { FeatureCard, PDFCard } from '../../components/common';
import {
  Sparkles,
  Zap,
  MessageSquareText,
  Microscope,
  HelpCircle,
  ShieldCheck,
  Cpu,
  Database,
} from 'lucide-react';

export const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'AI Summary',
      description: 'Get instant executive summaries, key hypothesis takeaways, and conclusion breakdowns in plain language.',
      badge: 'Fast',
    },
    {
      icon: <MessageSquareText className="w-6 h-6" />,
      title: 'Chat with PDF',
      description: 'Ask natural-language questions and receive grounded responses backed by exact page-number citations.',
      badge: 'RAG Grounded',
    },
    {
      icon: <Microscope className="w-6 h-6" />,
      title: 'Methodology Explanation',
      description: 'Deconstruct complex neural architectures, mathematical formulations, and evaluation metrics step-by-step.',
      badge: 'Deep Dive',
    },
    {
      icon: <HelpCircle className="w-6 h-6" />,
      title: 'Viva Question Generator',
      description: 'Prepare for thesis defenses and oral exams with AI-generated questions and model answers.',
      badge: 'Prep Tool',
    },
  ];

  const samplePapers = [
    {
      id: 'paper-attention-2026',
      title: 'Attention Is All You Need',
      filename: 'attention_is_all_you_need.pdf',
      fileSize: '2.4 MB',
      totalPages: 15,
      uploadDate: '2 hours ago',
    },
    {
      id: 'paper-gemini-flash-2026',
      title: 'Gemini 2.5: High Efficiency Multimodal Models',
      filename: 'gemini_2_5_tech_report.pdf',
      fileSize: '4.1 MB',
      totalPages: 32,
      uploadDate: 'Yesterday',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-600 selection:text-white">
      {/* Background glow effects */}
      <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-blue-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 relative z-10">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto mb-16 animate-fadeIn">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-950/80 border border-blue-800/60 text-xs font-semibold text-blue-400 mb-6 shadow-inner">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Next-Gen RAG Architecture</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Research<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">Pilot</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 font-normal leading-relaxed">
            Understand research papers faster using AI.
          </p>
        </div>

        {/* Drag & Drop Upload Section */}
        <div className="max-w-2xl mx-auto mb-20">
          <FileUploader />
        </div>

        {/* Sample Papers Quick Start */}
        <div className="mb-20">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                <span>Or explore sample research papers</span>
              </h2>
              <p className="text-xs text-slate-400 mt-1">Try ResearchPilot with pre-indexed landmark papers.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {samplePapers.map((paper) => (
              <PDFCard
                key={paper.id}
                title={paper.title}
                filename={paper.filename}
                fileSize={paper.fileSize}
                totalPages={paper.totalPages}
                uploadDate={paper.uploadDate}
                onClick={() => navigate(`/chat/${paper.id}`)}
              />
            ))}
          </div>
        </div>

        {/* Features Section */}
        <div className="mb-20">
          <div className="text-center max-w-xl mx-auto mb-12">
            <h2 className="text-2xl font-bold text-slate-100 mb-3">
              Purpose-built for serious academic research
            </h2>
            <p className="text-sm text-slate-400">
              Unlike generic PDF tools, ResearchPilot is calibrated for dense scientific papers, mathematical proofs, and complex tables.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <FeatureCard
                key={idx}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                badge={feature.badge}
                onClick={() => navigate('/chat/paper-attention-2026')}
              />
            ))}
          </div>
        </div>

        {/* Architecture Badges */}
        <div className="p-8 rounded-2xl bg-slate-900/40 border border-slate-800/80 flex flex-wrap items-center justify-around gap-6 text-slate-400 text-xs font-mono">
          <span className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-blue-400" /> PyMuPDF Extraction
          </span>
          <span>•</span>
          <span className="flex items-center gap-2">
            <Database className="w-4 h-4 text-indigo-400" /> FAISS Vector Index
          </span>
          <span>•</span>
          <span className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" /> Gemini 2.5 Flash
          </span>
          <span>•</span>
          <span className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-amber-400" /> Zero Data Retention
          </span>
        </div>
      </div>
    </div>
  );
};
