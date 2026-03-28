import type { Metadata } from "next";
import Link from "next/link";
import { MessageSquare, FileText } from "lucide-react";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Knowledge Assistant",
  description: "Company knowledge assistant powered by RAG",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="h-screen flex">
        <nav className="w-16 bg-primary flex flex-col items-center py-4 gap-4">
          <Link
            href="/chat"
            className="p-3 rounded-lg text-primary-foreground hover:bg-white/10 transition-colors"
            title="Chat"
          >
            <MessageSquare className="w-6 h-6" />
          </Link>
          <Link
            href="/docs"
            className="p-3 rounded-lg text-primary-foreground hover:bg-white/10 transition-colors"
            title="Documents"
          >
            <FileText className="w-6 h-6" />
          </Link>
        </nav>
        <main className="flex-1 overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
