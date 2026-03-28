"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getConversation } from "@/lib/api";
import { ChatContent } from "../chat-content";
import type { Message } from "@/lib/types";

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
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <p className="text-sm">Loading conversation...</p>
      </div>
    );
  }

  return <ChatContent conversationId={id} initialMessages={messages} />;
}
