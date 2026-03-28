import type { Conversation } from "@/lib/types";
import { ChatSidebar } from "@/components/chat/chat-sidebar";
import { Suspense } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchConversations(): Promise<Conversation[]> {
  const res = await fetch(`${API_URL}/api/conversations`, {
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

export default async function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const conversations = await fetchConversations();

  return (
    <div className="h-full flex">
      <ChatSidebar initialConversations={conversations} />
      {children}
    </div>
  );
}
