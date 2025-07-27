'use client';

export default function StatusTracker() {
  return (
    <div className="mt-4 flex items-center justify-center gap-3 p-3 bg-blue-100 text-blue-800 rounded-md">
      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
      <span>Analyzing... This may take a moment.</span>
    </div>
  );
}
