import { ReactNode } from 'react';

export interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  badge?: string;
  onClick?: () => void;
}

export const FeatureCard = ({ icon, title, description, badge, onClick }: FeatureCardProps) => {
  return (
    <div
      onClick={onClick}
      className="group relative p-6 rounded-2xl bg-slate-900/60 border border-slate-800/80 hover:border-blue-500/50 hover:bg-slate-900 transition-all duration-300 shadow-lg hover:shadow-2xl hover:shadow-blue-500/10 cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/60 group-hover:border-blue-500/40 group-hover:bg-blue-950/40 text-blue-400 flex items-center justify-center transition-all group-hover:scale-110">
            {icon}
          </div>
          {badge && (
            <span className="px-2.5 py-1 rounded-full bg-blue-950/80 border border-blue-800/50 text-[10px] font-semibold text-blue-400 tracking-wider uppercase">
              {badge}
            </span>
          )}
        </div>
        <h3 className="text-base font-semibold text-slate-100 group-hover:text-blue-300 transition-colors">
          {title}
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed mt-2">{description}</p>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/40 flex items-center text-xs font-medium text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
        <span>Try this feature</span>
        <span className="ml-1 group-hover:translate-x-1 transition-transform">→</span>
      </div>
    </div>
  );
};
