"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getConversation } from "@/lib/api";
import { ChatContent } from "../chat-content";
import { Skeleton } from "@/components/ui/skeleton";
import type { Message } from "@/lib/types";

function MessageSkeleton({ isUser }: { isUser: boolean }) {
  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : ""}`}>
      {!isUser && <Skeleton className="w-8 h-8 rounded-full shrink-0" />}
      <div className={`space-y-2 ${isUser ? "items-end" : ""}`}>
        <Skeleton className={`h-8 rounded-lg ${isUser ? "w-48" : "w-72"}`} />
      </div>
      {isUser && <Skeleton className="w-8 h-8 rounded-full shrink-0" />}
    </div>
  );
}

export default function ConversationPage() {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getConversation(id)
      .then((detail) => setMessages(detail.messages))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <div className="max-w-3xl mx-auto p-4 space-y-4 w-full">
          <MessageSkeleton isUser />
          <MessageSkeleton isUser={false} />
          <MessageSkeleton isUser />
          <MessageSkeleton isUser={false} />
        </div>
      </div>
    );
  }

  return <ChatContent conversationId={id} initialMessages={messages} />;
}
