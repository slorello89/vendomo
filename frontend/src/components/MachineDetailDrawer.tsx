import { useEffect, useState } from "react";
import { api } from "../api";
import type { MachineDetail } from "../types";
import { formatDate, formatDateTime, statusLabel } from "../util";
import StatusBadge from "./StatusBadge";

interface Props {
  machineId: string | null;
  onClose: () => void;
}

export default function MachineDetailDrawer({ machineId, onClose }: Props) {
  const [machine, setMachine] = useState<MachineDetail | null>(null);
  const [loading, setLoading] = useState(false);

  // Service form
  const [type, setType] = useState("inspection");
  const [technician, setTechnician] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const load = (id: string) => {
    setLoading(true);
    api
      .machine(id)
      .then(setMachine)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (!machineId) {
      setMachine(null);
      return;
    }
    load(machineId);
  }, [machineId]);

  if (!machineId) return null;

  const recordService = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!machineId || !technician) {
      setErr("Technician is required.");
      return;
    }
    setSaving(true);
    setErr(null);
    try {
      await api.createServiceLog({ machine_id: machineId, type, technician, notes });
      setTechnician("");
      setNotes("");
      load(machineId);
    } catch (e2) {
      setErr(String(e2));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="drawer-backdrop" onClick={onClose} />
      <aside className="drawer">
        <div className="drawer-header">
          <h2>{machine ? machine.name : "Loading…"}</h2>
          <button className="close-btn" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        {loading && <p className="muted">Loading…</p>}

        {machine && (
          <>
            <StatusBadge status={machine.status} />

            {machine.location_description && (
              <p className="muted" style={{ margin: "10px 0 0" }}>
                📍 {machine.location_description}
              </p>
            )}

            <div className="kv">
              <span className="k">Asset tag</span>
              <span>{machine.asset_tag}</span>
              <span className="k">Model</span>
              <span>
                {machine.manufacturer} {machine.model}
              </span>
              <span className="k">Location</span>
              <span>
                {machine.address ? `${machine.address}, ` : ""}
                {machine.city}, {machine.region}
              </span>
              <span className="k">Coordinates</span>
              <span>
                {machine.latitude.toFixed(4)}, {machine.longitude.toFixed(4)}
              </span>
              <span className="k">Capacity</span>
              <span>{machine.capacity} slots</span>
              <span className="k">Installed</span>
              <span>{formatDate(machine.installed_at)}</span>
              <span className="k">Last serviced</span>
              <span>{formatDate(machine.last_serviced_at)}</span>
            </div>

            <h2 style={{ fontSize: 15, marginTop: 16 }}>Record service visit</h2>
            {err && <div className="notice err">{err}</div>}
            <form onSubmit={recordService}>
              <div className="toolbar" style={{ marginBottom: 8 }}>
                <select value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="inspection">Inspection</option>
                  <option value="refill">Refill</option>
                  <option value="repair">Repair</option>
                </select>
                <input
                  placeholder="Technician"
                  value={technician}
                  onChange={(e) => setTechnician(e.target.value)}
                />
              </div>
              <textarea
                placeholder="Notes (optional)"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                style={{ width: "100%", marginBottom: 8 }}
              />
              <button type="submit" disabled={saving}>
                {saving ? "Saving…" : "Log service visit"}
              </button>
            </form>

            <h2 style={{ fontSize: 15, marginTop: 20 }}>Service history</h2>
            {machine.recent_service_logs.length === 0 && (
              <p className="muted">No service history yet.</p>
            )}
            {machine.recent_service_logs.map((log) => (
              <div key={log.id} className="log-item">
                <div>
                  <strong>{statusLabel(log.type)}</strong> — {log.technician}
                </div>
                <div className="meta">
                  {formatDateTime(log.created_at)}
                  {log.notes ? ` — ${log.notes}` : ""}
                </div>
              </div>
            ))}
          </>
        )}
      </aside>
    </>
  );
}
