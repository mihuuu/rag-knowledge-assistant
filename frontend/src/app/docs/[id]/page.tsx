"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getDocuments } from "@/lib/api";
import { DocumentDetail } from "@/components/docs/document-detail";
import type { Document } from "@/lib/types";

export default function DocDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDocuments()
      .then((docs) => {
        const match = docs.find((d) => d.id === id);
        setDocument(match ?? null);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <p className="text-sm">Loading document...</p>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted-foreground">
        <p className="text-sm">Document not found</p>
      </div>
    );
  }

  return <DocumentDetail document={document} />;
}
