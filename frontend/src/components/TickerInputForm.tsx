"use client";

import { useState, FormEvent } from "react";

interface Props {
  onSubmit: (ticker: string, filingType: string) => void;
  isLoading: boolean;
}

const filingTypes = ["10-K", "10-Q", "8-K"];

export default function TickerInputForm({ onSubmit, isLoading }: Props) {
  const [ticker, setTicker] = useState("");
  const [filingType, setFilingType] = useState("10-K");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (ticker.trim()) {
      onSubmit(ticker.trim().toUpperCase(), filingType);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col sm:flex-row gap-2 w-full"
    >
      <input
        type="text"
        value={ticker}
        onChange={(e) => setTicker(e.target.value)}
        placeholder="Enter Ticker (e.g., AAPL)"
        className="flex-grow p-3 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none text-black placeholder-gray-500"
        disabled={isLoading}
      />
      <select
        value={filingType}
        onChange={(e) => setFilingType(e.target.value)}
        className="p-3 border border-gray-300 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white text-gray-800"
        disabled={isLoading}
      >
        {filingTypes.map((type) => (
          <option key={type} value={type}>
            {type}
          </option>
        ))}
      </select>
      <button
        type="submit"
        className="bg-blue-600 text-white font-bold py-3 px-6 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        disabled={isLoading}
      >
        {isLoading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}
