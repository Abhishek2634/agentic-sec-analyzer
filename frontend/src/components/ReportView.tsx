'use client';

import { IReportData } from '@/lib/types';
import QaInterface from './QaInterface';

interface Props {
  report: IReportData;
}

export default function ReportView({ report }: Props) {
  const downloadJSON = () => {
    const jsonString = JSON.stringify(report, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${report.ticker}-${report.filingType}-report.json`; 
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  return (
    <div className="mt-8 p-6 bg-white rounded-lg shadow-md w-full animate-fade-in">
      <div className="flex justify-between items-center mb-6 pb-4 border-b">
        <h2 className="text-3xl font-bold text-gray-900">
          Analysis for {report.ticker} ({report.filingType})
        </h2>
        <div>
          <button 
            onClick={downloadJSON} 
            className="text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md"
          >
            Download JSON
          </button>
        </div>
      </div>

      <div className="space-y-8">
        <section>
          <h3 className="text-2xl font-semibold mb-3 text-gray-800">Executive Summary</h3>
          <p className="text-gray-600 whitespace-pre-wrap leading-relaxed">{report.executiveSummary}</p>
        </section>
        
        <section>
            <h3 className="text-2xl font-semibold mb-3 text-gray-800">Financial KPIs</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-gray-100 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-500">Total Revenue</h4>
                    <p className="text-2xl font-bold text-gray-900">{report.financialKPIs.total_revenue || 'N/A'}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-500">Net Income</h4>
                    <p className="text-2xl font-bold text-gray-900">{report.financialKPIs.net_income || 'N/A'}</p>
                </div>
                <div className="p-4 bg-gray-100 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-500">Earnings Per Share (EPS)</h4>
                    <p className="text-2xl font-bold text-gray-900">{report.financialKPIs.eps || 'N/A'}</p>
                </div>
            </div>
        </section>
        
        <section>
          <h3 className="text-2xl font-semibold mb-3 text-gray-800">Key Risk Factors</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-600">
            {report.riskFactors.map((risk, index) => (
              <li key={index} className="ml-2">{risk}</li>
            ))}
          </ul>
        </section>

        <section>
          <h3 className="text-2xl font-semibold mb-4 text-gray-800">Ask a Question</h3>
          <QaInterface ticker={report.ticker} />
        </section>
      </div>
    </div>
  );
}
