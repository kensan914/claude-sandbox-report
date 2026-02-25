import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  DRAFT: {
    label: "下書き",
    className: "bg-gray-100 text-gray-700 border-gray-200",
  },
  SUBMITTED: {
    label: "提出済み",
    className: "bg-blue-100 text-blue-700 border-blue-200",
  },
  REVIEWED: {
    label: "確認済み",
    className: "bg-green-100 text-green-700 border-green-200",
  },
};

export function ReportStatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? {
    label: status,
    className: "",
  };

  return (
    <Badge variant="outline" className={cn("font-medium", config.className)}>
      {config.label}
    </Badge>
  );
}
