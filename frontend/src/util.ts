export function statusColor(status: string): string {
  switch (status) {
    case "operational":
      return "#16a34a";
    case "needs_service":
      return "#f59e0b";
    case "offline":
      return "#dc2626";
    default:
      return "#64748b";
  }
}

export function statusLabel(status: string): string {
  return status.replace(/_/g, " ");
}

export function formatDate(iso: string | null): string {
  if (!iso) return "Never";
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
