'use client';

import { useState } from 'react';
import TickerInputForm from '@/components/TickerInputForm';
import ReportView from '@/components/ReportView';
import StatusTracker from '@/components/StatusTracker';
import { IReportData } from '@/lib/types';

export default function Home() {
  const [report, setReport] = useState<IReportData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateReport = async (ticker: string, filingType: string) => {
    setIsLoading(true);
    setError(null);
    setReport(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/generate-report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker: ticker, filing_type: filingType }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to generate report');
      }

      const data: IReportData = await response.json();
      setReport(data);
    } catch (err) {
      // --- THIS IS THE FIX ---
      // We check if the caught item is an instance of Error before accessing .message
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-4 sm:p-12 md:p-24 bg-gray-50">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Agentic AI SEC Filing Analysis
        </h1>
        <p className="text-center text-gray-500 mb-8">
          Enter a company ticker and select a filing type to get an AI-powered analysis.
        </p>
      </div>

      <div className="w-full max-w-2xl">
        <TickerInputForm onSubmit={handleGenerateReport} isLoading={isLoading} />
        {isLoading && <StatusTracker />}
        {error && <div className="mt-4 text-center text-red-500 bg-red-100 p-3 rounded-md">{error}</div>}
        {report && <ReportView report={report} />}
      </div>
    </main>
  );
}
