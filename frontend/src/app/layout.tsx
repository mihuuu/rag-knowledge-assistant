import type { Metadata } from "next";
import Link from "next/link";
import { MessageSquare, FileText, Bot } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Knowledge Assistant",
  description: "Company knowledge assistant powered by RAG",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="h-screen flex flex-col">
        <nav className="h-12 bg-primary flex items-center shrink-0">
          <span className="w-72 flex items-center ps-4 gap-2 text-primary-foreground font-semibold text-sm shrink-0">
            <Bot className="w-5 h-5" />
            Knowledge Assistant
          </span>
          <Link
            href="/chat"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-primary-foreground hover:bg-white/10 transition-colors text-sm"
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </Link>
          <Link
            href="/docs"
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-primary-foreground hover:bg-white/10 transition-colors text-sm"
          >
            <FileText className="w-4 h-4" />
            Documents
          </Link>
        </nav>
        <main className="flex-1 overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
