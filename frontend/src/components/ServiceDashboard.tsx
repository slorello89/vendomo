import { useEffect, useState } from "react";
import { api } from "../api";
import type { ServiceLog, Stats } from "../types";
import { useSelection } from "../context";
import { formatDateTime, statusColor, statusLabel } from "../util";

export default function ServiceDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [logs, setLogs] = useState<ServiceLog[]>([]);
  const { open } = useSelection();

  useEffect(() => {
    api.stats().then(setStats).catch((e) => console.error(e));
    api.serviceLogs({ limit: 30 }).then(setLogs).catch((e) => console.error(e));
  }, []);

  const topRegions = stats
    ? Object.entries(stats.by_region).slice(0, 8)
    : [];

  return (
    <div className="page">
      <h1>Service dashboard</h1>

      <div className="cards">
        <div className="card">
          <div className="value">{stats?.total_machines.toLocaleString() ?? "—"}</div>
          <div className="label">Total machines</div>
        </div>
        <div className="card">
          <div className="value" style={{ color: statusColor("needs_service") }}>
            {stats?.needs_service.toLocaleString() ?? "—"}
          </div>
          <div className="label">Need service</div>
        </div>
        <div className="card">
          <div className="value" style={{ color: statusColor("offline") }}>
            {stats?.by_status.offline?.toLocaleString() ?? "0"}
          </div>
          <div className="label">Offline</div>
        </div>
        <div className="card">
          <div className="value">{stats?.never_serviced.toLocaleString() ?? "—"}</div>
          <div className="label">Never serviced</div>
        </div>
      </div>

      <div className="columns">
        <div className="panel">
          <h2>Fleet by status</h2>
          <table>
            <tbody>
              {stats &&
                Object.entries(stats.by_status).map(([s, n]) => (
                  <tr key={s} style={{ cursor: "default" }}>
                    <td>
                      <span
                        className="legend"
                        style={{ position: "static", padding: 0, border: "none", background: "none" }}
                      >
                        <span className="dot" style={{ background: statusColor(s) }} />
                        {statusLabel(s)}
                      </span>
                    </td>
                    <td style={{ textAlign: "right" }}>{n.toLocaleString()}</td>
                  </tr>
                ))}
            </tbody>
          </table>

          <h2 style={{ marginTop: 20 }}>Top regions</h2>
          <table>
            <tbody>
              {topRegions.map(([r, n]) => (
                <tr key={r} style={{ cursor: "default" }}>
                  <td>{r}</td>
                  <td style={{ textAlign: "right" }}>{n.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <h2>Recent service activity</h2>
          {logs.length === 0 && <p className="muted">No service logs yet.</p>}
          {logs.map((log) => (
            <div
              key={log.id}
              className="log-item"
              style={{ cursor: "pointer" }}
              onClick={() => open(log.machine_id)}
            >
              <div>
                <strong>{statusLabel(log.type)}</strong> by {log.technician}
              </div>
              <div className="meta">
                {formatDateTime(log.created_at)}
                {log.notes ? ` — ${log.notes}` : ""}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
