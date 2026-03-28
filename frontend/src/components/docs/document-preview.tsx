"use client";

import { useEffect, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { getDocumentPreviewUrl } from "@/lib/api";
import type { Document } from "@/lib/types";

interface DocumentPreviewProps {
  document: Document | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function DocumentPreview({ document, open, onOpenChange }: DocumentPreviewProps) {
  const [textContent, setTextContent] = useState<string>("");

  useEffect(() => {
    if (!document || !open) return;
    if (document.file_type === "md" || document.file_type === "txt") {
      fetch(getDocumentPreviewUrl(document.id))
        .then((res) => res.text())
        .then(setTextContent)
        .catch(console.error);
    }
  }, [document, open]);

  if (!document) return null;

  const previewUrl = getDocumentPreviewUrl(document.id);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>{document.filename}</DialogTitle>
        </DialogHeader>
        <div className="flex-1 overflow-auto min-h-[400px]">
          {document.file_type === "pdf" ? (
            <iframe src={previewUrl} className="w-full h-[70vh] rounded border" title={document.filename} />
          ) : document.file_type === "md" || document.file_type === "txt" ? (
            <pre className="whitespace-pre-wrap text-sm bg-muted rounded p-4 overflow-auto max-h-[70vh]">
              {textContent}
            </pre>
          ) : (
            <div className="flex flex-col items-center justify-center h-[200px] text-muted-foreground">
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
      </DialogContent>
    </Dialog>
  );
}
