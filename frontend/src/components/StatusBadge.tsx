import { statusColor, statusLabel } from "../util";

export default function StatusBadge({ status }: { status: string }) {
  return (
    <span className="badge" style={{ background: statusColor(status) }}>
      {statusLabel(status)}
    </span>
  );
}
