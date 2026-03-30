"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronRight, Folder, FolderOpen, FileText, FileType, FileCode, File } from "lucide-react";
import type { Document } from "@/lib/types";

const categoryLabels: Record<string, string> = {
  handbooks: "Handbooks",
  policies: "Policies",
  faqs: "FAQs",
  guides: "Guides",
  announcements: "Announcements",
};

const fileIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  pdf: FileText,
  docx: FileType,
  md: FileCode,
  txt: File,
};

interface FileTreeProps {
  documents: Document[];
}

export function FileTree({ documents }: FileTreeProps) {
  const pathname = usePathname();
  const grouped = documents.reduce<Record<string, Document[]>>((acc, doc) => {
    const cat = doc.category || "other";
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(doc);
    return acc;
  }, {});

  const categories = Object.keys(grouped).sort();

  const [expanded, setExpanded] = useState<Set<string>>(new Set(categories));

  const toggleCategory = (cat: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  };

  return (
    <div className="w-72 border-r bg-muted/30 flex flex-col h-full overflow-auto">
      <div className="p-3">
        <h2 className="text-sm font-semibold">Documents</h2>
        <p className="text-xs text-muted-foreground mt-0.5">{documents.length} files</p>
      </div>
      <div className="p-2">
        {categories.map((cat) => {
          const isExpanded = expanded.has(cat);
          const docs = grouped[cat];
          return (
            <div key={cat} className="mb-1">
              <button
                onClick={() => toggleCategory(cat)}
                className="flex items-center gap-1.5 w-full px-2 py-1.5 text-sm rounded-md hover:bg-accent/50 transition-colors"
              >
                <ChevronRight
                  className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${
                    isExpanded ? "rotate-90" : ""
                  }`}
                />
                {isExpanded ? (
                  <FolderOpen className="w-4 h-4 text-muted-foreground" />
                ) : (
                  <Folder className="w-4 h-4 text-muted-foreground" />
                )}
                <span className="font-medium">{categoryLabels[cat] || cat}</span>
              </button>
              {isExpanded && (
                <div className="ml-3 pl-3 border-l border-border">
                  {docs.map((doc) => {
                    const Icon = fileIcons[doc.file_type] || File;
                    const isSelected = pathname === `/docs/${doc.id}`;
                    return (
                      <Link
                        key={doc.id}
                        href={`/docs/${doc.id}`}
                        className={`flex items-center gap-2 w-full px-2 py-1.5 text-sm rounded-md transition-colors ${
                          isSelected
                            ? "bg-accent text-accent-foreground"
                            : "hover:bg-accent/50"
                        }`}
                      >
                        <Icon className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                        <span className="truncate">{doc.filename}</span>
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
        {documents.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">No documents yet</p>
        )}
      </div>
    </div>
  );
}
