import { Link } from 'react-router-dom';
import { Button } from '../../components/common';
import { BookOpenText, Home } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
      <div className="w-20 h-20 rounded-3xl bg-blue-950/60 border border-blue-800/40 flex items-center justify-center text-blue-400 mb-6 shadow-2xl animate-bounce">
        <BookOpenText className="w-10 h-10" />
      </div>

      <h1 className="text-7xl font-extrabold text-white tracking-tight mb-2">404</h1>
      <h2 className="text-xl font-semibold text-slate-300 mb-4">Research Paper Not Found</h2>
      <p className="text-sm text-slate-400 max-w-md mb-8 leading-relaxed">
        The page or research document session you are looking for has expired or does not exist in the index.
      </p>

      <div className="flex items-center gap-4">
        <Link to="/">
          <Button variant="primary" leftIcon={<Home className="w-4 h-4" />}>
            Back to Home
          </Button>
        </Link>
      </div>
    </div>
  );
};
