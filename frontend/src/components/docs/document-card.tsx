"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, FileType, FileCode, File } from "lucide-react";
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

interface DocumentCardProps {
  document: Document;
  onClick: () => void;
}

export function DocumentCard({ document, onClick }: DocumentCardProps) {
  const Icon = fileIcons[document.file_type] || File;
  const colorClass = categoryColors[document.category] || "bg-gray-100 text-gray-800";

  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center shrink-0">
            <Icon className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="font-medium text-sm truncate">{document.filename}</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={`${colorClass} border-0 text-[10px]`}>{document.category}</Badge>
              <span className="text-xs text-muted-foreground">{formatFileSize(document.file_size)}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{document.chunk_count} chunks</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
