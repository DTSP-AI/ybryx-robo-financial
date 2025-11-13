"use client";

import { useState, useRef, useEffect } from "react";
import { X, MessageCircle, Send, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

interface ChatWidgetProps {
  apiUrl?: string;
}

export default function ChatWidget({ apiUrl = process.env.NEXT_PUBLIC_API_URL }: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm Alex from Ybryx Capital. I help businesses access robotics equipment without the upfront capital burden. What brings you here today?",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
          conversation_history: messages,
        }),
      });

      const data = await response.json();

      if (data.success && data.data) {
        const assistantMessage: Message = {
          role: "assistant",
          content: data.data.message,
          timestamp: data.data.timestamp,
        };

        setMessages((prev) => [...prev, assistantMessage]);

        // Store session ID
        if (data.data.session_id && !sessionId) {
          setSessionId(data.data.session_id);
        }
      } else {
        throw new Error(data.error || "Failed to get response");
      }
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment or contact us directly at contact@ybryxcapital.com",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-black hover:bg-neutral-800 text-white rounded-full p-4 shadow-lg transition-all hover:scale-110 z-50 flex items-center gap-2"
        aria-label="Open chat"
      >
        <MessageCircle className="w-6 h-6" />
        <span className="hidden sm:inline text-sm font-medium">Chat with Alex</span>
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-8rem)] bg-white rounded-lg shadow-2xl border border-neutral-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-black text-white p-4 rounded-t-lg flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
            <span className="text-black font-bold text-lg">A</span>
          </div>
          <div>
            <h3 className="font-semibold">Alex</h3>
            <p className="text-xs text-neutral-300">Ybryx Capital Sales Agent</p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="hover:bg-neutral-800 p-1 rounded transition-colors"
          aria-label="Close chat"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === "user"
                  ? "bg-black text-white"
                  : "bg-neutral-100 text-neutral-900"
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.timestamp && (
                <p className={`text-xs mt-1 ${
                  message.role === "user" ? "text-neutral-300" : "text-neutral-500"
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-neutral-100 rounded-lg p-3">
              <Loader2 className="w-5 h-5 animate-spin text-neutral-600" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-neutral-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about equipment, leasing, or prequalification..."
            className="flex-1 border border-neutral-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="bg-black text-white rounded-lg px-4 py-2 hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Send message"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-neutral-500 mt-2">
          Powered by GPT-5-nano • Instant responses
        </p>
      </div>
    </div>
  );
}
