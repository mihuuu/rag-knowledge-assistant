"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { getConversations, deleteConversation } from "@/lib/api";
import type { Conversation } from "@/lib/types";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function ChatSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const refresh = useCallback(async () => {
    try {
      const convs = await getConversations();
      setConversations(convs);
    } catch (err) {
      console.error("Failed to refresh conversations:", err);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Listen for custom event to refresh sidebar after new message
  useEffect(() => {
    const handler = () => refresh();
    window.addEventListener("conversations-updated", handler);
    return () => window.removeEventListener("conversations-updated", handler);
  }, [refresh]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    e.stopPropagation();
    await deleteConversation(id);
    await refresh();
    if (pathname === `/chat/${id}`) {
      router.push("/chat");
    }
  };

  return (
    <div className="w-72 max-w-72 border-r bg-muted/30 flex flex-col h-full">
      <div className="p-3 border-b">
        <Button asChild className="w-full" variant="outline">
          <Link href="/chat">
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Link>
        </Button>
      </div>
      <div className="p-2 space-y-1 overflow-y-auto flex-1">
        {conversations.map((conv) => {
          const isActive = pathname === `/chat/${conv.id}`;
          return (
            <Link
              key={conv.id}
              href={`/chat/${conv.id}`}
              className={`group flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${
                isActive ? "bg-accent text-accent-foreground" : "hover:bg-accent/50"
              }`}
            >
              {/* <MessageSquare className="w-4 h-4 shrink-0 text-muted-foreground" /> */}
              <div className="flex-1 min-w-0">
                <p className="truncate font-medium">{conv.title}</p>
                <p className="text-xs text-muted-foreground">{timeAgo(conv.updated_at)}</p>
              </div>
              <button
                onClick={(e) => handleDelete(e, conv.id)}
                className="shrink-0 opacity-0 group-hover:opacity-100 hover:text-destructive transition-all"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </Link>
          );
        })}
        {conversations.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">No conversations yet</p>
        )}
      </div>
    </div>
  );
}
