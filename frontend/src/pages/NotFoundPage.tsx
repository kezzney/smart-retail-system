import React from 'react';
import { Link } from 'react-router-dom';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm max-w-lg mx-auto mt-12">
      <div className="text-4xl mb-4">🔍</div>
      <h1 className="text-2xl font-bold text-slate-800">Page Not Found</h1>
      <p className="text-sm text-slate-500 mt-2 mb-6">
        The requested retail intelligence view or module route does not exist.
      </p>
      <Link
        to="/"
        className="inline-flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors"
      >
        Return to Dashboard
      </Link>
    </div>
  );
};
