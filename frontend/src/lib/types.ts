export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Source {
  document_id: string;
  filename: string;
  category: string;
  chunk_text: string;
  score: number;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: Source[] | null;
  created_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface Document {
  id: string;
  filename: string;
  category: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  ingested_at: string;
}
