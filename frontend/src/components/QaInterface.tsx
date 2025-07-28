"use client";

import { useState, FormEvent } from "react";
import { IMessage } from "@/lib/types";

interface Props {
  ticker: string;
}

export default function QaInterface({ ticker }: Props) {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage: IMessage = { sender: "user", text: query };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setQuery("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/qna`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ticker, question: query }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get an answer.");
      }
      const data = await response.json();
      const aiMessage: IMessage = { sender: "ai", text: data.answer };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {

      console.error("Q&A Error:", error);
      const errorMessage: IMessage = {
        sender: "ai",
        text: "Sorry, I encountered an error.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <div className="h-64 overflow-y-auto mb-4 p-2 space-y-4">
        {messages.length === 0 && (
          <p className="text-center text-gray-500">
            Ask a question about the filing, e.g., &quot;What were the total
            revenues?&quot;
          </p>
        )}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${
              msg.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`rounded-lg px-4 py-2 max-w-xs lg:max-w-md ${
                msg.sender === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-lg px-4 py-2 bg-gray-200 text-gray-800">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your question..."
          className="flex-grow p-2 border rounded-md focus:ring-2 focus:ring-blue-500 text-black placeholder-gray-500"
          disabled={isLoading}
        />

        <button
          type="submit"
          className="bg-blue-600 text-white font-bold py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          disabled={isLoading}
        >
          Send
        </button>
      </form>
    </div>
  );
}
