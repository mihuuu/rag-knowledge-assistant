import type { Document } from "@/lib/types";
import { FileTree } from "@/components/docs/file-tree";

const API_URL =
  process.env.SERVER_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_URL}/api/documents`, {
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}

export default async function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const documents = await fetchDocuments();

  return (
    <div className="h-full flex">
      <FileTree documents={documents} />
      {children}
    </div>
  );
}
