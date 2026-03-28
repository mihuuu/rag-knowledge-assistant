"use client";

import { useEffect, useRef, useState } from "react";
import { ChatMessage } from "@/components/chat/chat-message";
import { ChatInput } from "@/components/chat/chat-input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { sendMessage } from "@/lib/api";
import type { Message, Source } from "@/lib/types";

interface ChatContentProps {
  conversationId: string | null;
  initialMessages: Message[];
}

export function ChatContent({ conversationId, initialMessages }: ChatContentProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [streamingSources, setStreamingSources] = useState<Source[] | null>(null);
  const streamingSourcesRef = useRef<Source[] | null>(null);
  const streamingContentRef = useRef("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  const handleSend = async (message: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: message,
      sources: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);
    setStreamingContent("");
    setStreamingSources(null);

    try {
      await sendMessage(
        message,
        conversationId,
        (token) => {
          setStreamingContent((prev) => {
            const next = prev + token;
            streamingContentRef.current = next;
            return next;
          });
        },
        (sources) => {
          setStreamingSources(sources);
          streamingSourcesRef.current = sources;
        },
        (data) => {
          const assistantMsg: Message = {
            id: data.message_id,
            role: "assistant",
            content: streamingContentRef.current,
            sources: streamingSourcesRef.current,
            created_at: new Date().toISOString(),
          };
          setMessages((msgs) => [...msgs, assistantMsg]);
          setStreamingContent("");
          streamingContentRef.current = "";
          setIsStreaming(false);

          // Notify sidebar to refresh
          window.dispatchEvent(new Event("conversations-updated"));

          // Update URL without re-rendering the page
          if (!conversationId) {
            window.history.replaceState(null, "", `/chat/${data.conversation_id}`);
          }
        },
        (error) => {
          console.error("Stream error:", error);
          setIsStreaming(false);
        }
      );
    } catch (err) {
      console.error("Send error:", err);
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col">
      <ScrollArea className="flex-1">
        <div className="max-w-3xl mx-auto p-4 space-y-4">
          {messages.length === 0 && !isStreaming && (
            <div className="flex flex-col items-center justify-center h-[60vh] text-muted-foreground">
              <p className="text-lg font-medium">Company Knowledge Assistant</p>
              <p className="text-sm mt-1">Ask questions about company documents</p>
            </div>
          )}
          {messages.map((msg) => (
            <ChatMessage key={msg.id} role={msg.role} content={msg.content} sources={msg.sources} />
          ))}
          {isStreaming && streamingContent && (
            <ChatMessage
              role="assistant"
              content={streamingContent}
              sources={streamingSources}
              isStreaming
            />
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>
      <ChatInput onSend={handleSend} disabled={isStreaming} />
    </div>
  );
}
