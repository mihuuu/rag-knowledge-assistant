import { FileText } from "lucide-react";

export default function DocsPage() {
  return (
    <div className="flex-1 flex items-center justify-center text-muted-foreground">
      <div className="text-center">
        <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
        <p className="text-sm">Select a document to view its details</p>
      </div>
    </div>
  );
}
