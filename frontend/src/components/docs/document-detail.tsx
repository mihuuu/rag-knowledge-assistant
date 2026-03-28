"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { getDocumentPreviewUrl } from "@/lib/api";
import { FileText, FileType, FileCode, File, Download } from "lucide-react";
import type { Document } from "@/lib/types";

const categoryColors: Record<string, string> = {
  handbooks: "bg-blue-100 text-blue-800",
  policies: "bg-green-100 text-green-800",
  faqs: "bg-yellow-100 text-yellow-800",
  guides: "bg-purple-100 text-purple-800",
  announcements: "bg-red-100 text-red-800",
};

const fileIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  pdf: FileText,
  docx: FileType,
  md: FileCode,
  txt: File,
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

interface DocumentDetailProps {
  document: Document;
}

export function DocumentDetail({ document }: DocumentDetailProps) {
  const [textContent, setTextContent] = useState<string>("");

  useEffect(() => {
    setTextContent("");
    if (document.file_type === "md" || document.file_type === "txt") {
      fetch(getDocumentPreviewUrl(document.id))
        .then((res) => res.text())
        .then(setTextContent)
        .catch(console.error);
    }
  }, [document]);

  const Icon = fileIcons[document.file_type] || File;
  const colorClass = categoryColors[document.category] || "bg-gray-100 text-gray-800";
  const previewUrl = getDocumentPreviewUrl(document.id);

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <div className="p-3 border-b flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center shrink-0">
          <Icon className="w-5 h-5 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="font-semibold text-sm truncate">{document.filename}</h2>
          <div className="flex items-center gap-2 mt-0.5">
            <Badge className={`${colorClass} border-0 text-[10px]`}>{document.category}</Badge>
            <span className="text-xs text-muted-foreground">{formatFileSize(document.file_size)}</span>
          </div>
        </div>
        <a
          href={previewUrl}
          download
          className="p-2 rounded-md hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
          title="Download"
        >
          <Download className="w-4 h-4" />
        </a>
      </div>
      <div className="flex-1 overflow-auto p-4">
        {document.file_type === "pdf" ? (
          <iframe
            src={previewUrl}
            className="w-full h-full rounded border min-h-[500px]"
            title={document.filename}
          />
        ) : document.file_type === "md" || document.file_type === "txt" ? (
          <pre className="whitespace-pre-wrap text-sm bg-muted rounded p-4 h-full overflow-auto">
            {textContent}
          </pre>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
            <p>Preview not available for .{document.file_type} files</p>
            <a
              href={previewUrl}
              download
              className="mt-2 text-sm text-primary underline"
            >
              Download file
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
