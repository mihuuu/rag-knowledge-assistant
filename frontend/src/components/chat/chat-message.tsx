"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Bot } from "lucide-react";
import type { Source } from "@/lib/types";
import { SourceCard } from "./source-card";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  sources?: Source[] | null;
  isStreaming?: boolean;
}

export function ChatMessage({ role, content, sources, isStreaming }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : ""}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
          <Bot className="w-4 h-4 text-primary-foreground" />
        </div>
      )}
      <div className={`max-w-[75%] space-y-2 ${isUser ? "order-first" : ""}`}>
        <div
          className={`rounded-lg px-4 py-2.5 ${
            isUser ? "bg-primary text-primary-foreground ml-auto" : "bg-muted"
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : isStreaming && !content ? (
            <div className="flex items-center gap-1.5 text-muted-foreground text-sm py-0.5">
              <span className="animate-pulse">Thinking</span>
              <span className="flex gap-0.5">
                <span className="animate-bounce [animation-delay:0ms]">.</span>
                <span className="animate-bounce [animation-delay:150ms]">.</span>
                <span className="animate-bounce [animation-delay:300ms]">.</span>
              </span>
            </div>
          ) : (
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
              {isStreaming && <span className="inline-block w-2 h-4 bg-foreground/70 animate-pulse ml-0.5" />}
            </div>
          )}
        </div>
        {sources && sources.length > 0 && (() => {
          const unique = Object.values(
            sources.reduce<Record<string, Source>>((acc, s) => {
              const key = s.document_id;
              if (!acc[key] || s.score > acc[key].score) acc[key] = s;
              return acc;
            }, {})
          );
          return (
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground font-medium px-1">Sources</p>
              {unique.map((source) => (
                <SourceCard key={source.document_id} source={source} />
              ))}
            </div>
          );
        })()}
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
