export interface IReportData {
  ticker: string;
  filingType: string;
  executiveSummary: string;
  riskFactors: string[];
  sentiment: string;
  financialKPIs: Record<string, string>;
}

export interface IMessage {
  sender: 'user' | 'ai';
  text: string;
}
