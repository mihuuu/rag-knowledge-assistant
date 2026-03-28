import Link from "next/link";
import { ExternalLink, FileText } from "lucide-react";
import type { Source } from "@/lib/types";

export function SourceCard({ source }: { source: Source }) {
  return (
    <div className="w-full text-sm flex items-center gap-2 px-3 pt-1 text-muted-foreground">
      <ExternalLink className="w-3.5 h-3.5 shrink-0" />
      <Link
        href={`/docs/${source.document_id}`}
        className="truncate hover:underline"
      >
        {source.filename}
      </Link>
      {/* <Link href={`/docs/${source.document_id}`} className="shrink-0 text-muted-foreground hover:text-foreground">
        <ExternalLink className="w-3 h-3" />
      </Link> */}
    </div>
  );
}
