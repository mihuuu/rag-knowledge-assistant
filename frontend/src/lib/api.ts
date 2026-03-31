import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { Conversation, ConversationDetail, Document, Source } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// REST helpers
async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// Conversations
export async function getConversations(): Promise<Conversation[]> {
  return fetchJSON("/api/conversations");
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  return fetchJSON(`/api/conversations/${id}`);
}

export async function deleteConversation(id: string): Promise<void> {
  await fetch(`${API_URL}/api/conversations/${id}`, { method: "DELETE" });
}

// Documents
export async function getDocuments(): Promise<Document[]> {
  return fetchJSON("/api/documents");
}

export function getDocumentPreviewUrl(id: string): string {
  return `${API_URL}/api/documents/${id}/preview`;
}

export async function uploadDocument(
  file: File,
  category: string
): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  form.append("category", category);
  const res = await fetch(`${API_URL}/api/documents/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

export async function updateDocument(
  id: string,
  file: File,
  category?: string
): Promise<Document> {
  const form = new FormData();
  form.append("file", file);
  if (category) form.append("category", category);
  const res = await fetch(`${API_URL}/api/documents/${id}`, {
    method: "PUT",
    body: form,
  });
  if (!res.ok) throw new Error(`Update failed: ${res.status}`);
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/documents/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Delete failed: ${res.status}`);
}

// Chat (SSE streaming)
export async function sendMessage(
  message: string,
  conversationId: string | null,
  onToken: (token: string) => void,
  onSources: (sources: Source[]) => void,
  onDone: (data: { message_id: string; conversation_id: string }) => void,
  onError?: (error: Error) => void
): Promise<void> {
  const ctrl = new AbortController();
  await fetchEventSource(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
    signal: ctrl.signal,
    onmessage(ev) {
      if (ev.event === "token") {
        onToken(JSON.parse(ev.data).token);
      } else if (ev.event === "sources") {
        onSources(JSON.parse(ev.data));
      } else if (ev.event === "done") {
        onDone(JSON.parse(ev.data));
        ctrl.abort();
      }
    },
    onerror(err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      onError?.(err instanceof Error ? err : new Error(String(err)));
      throw err; // stop retrying
    },
  });
}
