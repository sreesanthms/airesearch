import React from 'react';
import { FileText } from 'lucide-react';

interface MarkdownRendererProps {
  content: string;
}

/**
 * Custom robust Markdown & Citation Badge Renderer.
 * Handles headings, bold, italics, mixed lists, code blocks, blockquotes, dividers, and [Page X] badges.
 */
export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  if (!content) return null;

  const parseInline = (text: string): React.ReactNode[] => {
    // Regex matching [Page X] or [Page X, Y] badges, **bold**, `code`, *italics*
    const tokenRegex = /(\[Page\s+\d+(?:,\s*\d+)*\]|\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/gi;
    const parts = text.split(tokenRegex);

    return parts.map((part, idx) => {
      if (!part) return null;

      // Citation badge [Page X]
      const pageMatch = part.match(/^\[Page\s+(\d+(?:,\s*\d+)*)\]$/i);
      if (pageMatch) {
        return (
          <span
            key={idx}
            className="inline-flex items-center gap-1 px-2 py-0.5 mx-1 rounded-md bg-blue-950/80 border border-blue-700/60 text-blue-300 font-mono text-[11px] font-semibold shadow-sm hover:bg-blue-900/60 transition-colors"
          >
            <FileText className="w-3 h-3 text-blue-400 shrink-0" />
            <span>Page {pageMatch[1]}</span>
          </span>
        );
      }

      // **Bold**
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={idx} className="font-semibold text-slate-100">
            {part.slice(2, -2)}
          </strong>
        );
      }

      // `Code`
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code
            key={idx}
            className="px-1.5 py-0.5 mx-0.5 rounded bg-slate-950 border border-slate-800 text-blue-300 font-mono text-xs"
          >
            {part.slice(1, -1)}
          </code>
        );
      }

      // *Italics*
      if (part.startsWith('*') && part.endsWith('*')) {
        return (
          <em key={idx} className="italic text-slate-300">
            {part.slice(1, -1)}
          </em>
        );
      }

      return part;
    });
  };

  // Process blocks
  const blocks = content.split(/\n\n+/);

  return (
    <div className="space-y-3 text-slate-200 text-sm leading-relaxed">
      {blocks.map((block, bIdx) => {
        const trimmedBlock = block.trim();
        if (!trimmedBlock) return null;

        // Divider --- or ***
        if (trimmedBlock === '---' || trimmedBlock === '***') {
          return <hr key={bIdx} className="my-4 border-slate-800/80" />;
        }

        // Code Block ```
        if (trimmedBlock.startsWith('```')) {
          const lines = trimmedBlock.split('\n');
          const codeLines = lines.slice(1, lines.length - 1);
          return (
            <pre
              key={bIdx}
              className="p-4 my-3 rounded-xl bg-slate-950 border border-slate-800 text-blue-200 font-mono text-xs overflow-x-auto shadow-lg"
            >
              <code>{codeLines.join('\n')}</code>
            </pre>
          );
        }

        // Line-by-line block parser
        const lines = trimmedBlock.split('\n');
        const elements: React.ReactNode[] = [];

        for (let lIdx = 0; lIdx < lines.length; lIdx++) {
          const line = lines[lIdx].trim();
          if (!line) continue;

          // H1 #
          if (line.startsWith('# ')) {
            elements.push(
              <h1 key={`${bIdx}-${lIdx}`} className="text-lg font-bold text-slate-100 mt-4 mb-2 pb-1 border-b border-slate-800">
                {parseInline(line.slice(2))}
              </h1>
            );
            continue;
          }

          // H2 ##
          if (line.startsWith('## ')) {
            elements.push(
              <h2 key={`${bIdx}-${lIdx}`} className="text-base font-bold text-blue-300 mt-4 mb-2">
                {parseInline(line.slice(3))}
              </h2>
            );
            continue;
          }

          // H3 ###
          if (line.startsWith('### ')) {
            elements.push(
              <h3 key={`${bIdx}-${lIdx}`} className="text-sm font-semibold text-blue-400 mt-3 mb-1.5 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0"></span>
                {parseInline(line.slice(4))}
              </h3>
            );
            continue;
          }

          // Blockquote >
          if (line.startsWith('> ')) {
            elements.push(
              <blockquote
                key={`${bIdx}-${lIdx}`}
                className="p-3 my-2 rounded-xl bg-slate-950/80 border-l-4 border-blue-500 text-xs text-slate-300 italic shadow-inner"
              >
                {parseInline(line.slice(2))}
              </blockquote>
            );
            continue;
          }

          // Bullet List Item (- or *)
          if (line.startsWith('- ') || line.startsWith('* ')) {
            const itemText = line.slice(2);
            elements.push(
              <div key={`${bIdx}-${lIdx}`} className="flex items-start gap-2.5 my-1.5 pl-1 text-slate-200">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-2 shrink-0 opacity-90" />
                <span className="flex-1 leading-relaxed">{parseInline(itemText)}</span>
              </div>
            );
            continue;
          }

          // Numbered List Item (1. 2. 3.)
          const numMatch = line.match(/^(\d+)\.\s+(.*)/);
          if (numMatch) {
            elements.push(
              <div key={`${bIdx}-${lIdx}`} className="flex items-start gap-2.5 my-1.5 pl-1 text-slate-200">
                <span className="px-1.5 py-0.5 rounded bg-blue-950/90 border border-blue-800/70 text-blue-400 font-mono text-[11px] font-bold shrink-0">
                  {numMatch[1]}
                </span>
                <span className="flex-1 leading-relaxed">{parseInline(numMatch[2])}</span>
              </div>
            );
            continue;
          }

          // Standard paragraph text line
          elements.push(
            <p key={`${bIdx}-${lIdx}`} className="my-1 leading-relaxed">
              {parseInline(line)}
            </p>
          );
        }

        return <div key={bIdx} className="space-y-1">{elements}</div>;
      })}
    </div>
  );
};
