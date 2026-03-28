import Link from "next/link";
import { ExternalLink, FileText } from "lucide-react";
import type { Source } from "@/lib/types";

export function SourceCard({ source }: { source: Source }) {
  return (
    <div className="border rounded-md text-sm">
      <div className="w-full flex items-center gap-2 px-3 py-2">
        <FileText className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
        <Link
          href={`/docs/${source.document_id}`}
          className="truncate font-medium hover:underline"
        >
          {source.filename}
        </Link>
        <Link href={`/docs/${source.document_id}`} className="shrink-0 text-muted-foreground hover:text-foreground">
          <ExternalLink className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}
