"use client";

import { ChatSidebar } from "@/components/chat/chat-sidebar";

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="h-full flex">
      <ChatSidebar />
      {children}
    </div>
  );
}
