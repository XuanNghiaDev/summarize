import React from 'react';

export default function LoadingSpinner() {
  return (
    <div className="flex items-center gap-3">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-sky-600 border-t-transparent" />
      <div className="text-sm text-slate-600">Generating...</div>
    </div>
  );
}
