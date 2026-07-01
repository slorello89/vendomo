import { useEffect, useState } from "react";
import { api } from "../api";
import type { Machine, Stats } from "../types";
import { useSelection } from "../context";
import { formatDate } from "../util";
import StatusBadge from "./StatusBadge";

const PAGE = 25;

export default function ListView() {
  const [items, setItems] = useState<Machine[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [status, setStatus] = useState("");
  const [region, setRegion] = useState("");
  const [q, setQ] = useState("");
  const [regions, setRegions] = useState<string[]>([]);
  const { open } = useSelection();

  useEffect(() => {
    api
      .stats()
      .then((s: Stats) => setRegions(Object.keys(s.by_region).sort()))
      .catch((e) => console.error(e));
  }, []);

  useEffect(() => {
    api
      .machines({
        limit: PAGE,
        offset,
        status: status || undefined,
        region: region || undefined,
        q: q || undefined,
      })
      .then((r) => {
        setItems(r.items);
        setTotal(r.total);
      })
      .catch((e) => console.error(e));
  }, [offset, status, region, q]);

  const reset = () => setOffset(0);

  return (
    <div className="page">
      <h1>Machines</h1>

      <div className="toolbar">
        <input
          placeholder="Search by name…"
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            reset();
          }}
          style={{ minWidth: 220 }}
        />
        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            reset();
          }}
        >
          <option value="">All statuses</option>
          <option value="operational">Operational</option>
          <option value="needs_service">Needs service</option>
          <option value="offline">Offline</option>
        </select>
        <select
          value={region}
          onChange={(e) => {
            setRegion(e.target.value);
            reset();
          }}
        >
          <option value="">All regions</option>
          {regions.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      <table>
        <thead>
          <tr>
            <th>Asset tag</th>
            <th>Name</th>
            <th>City</th>
            <th>Region</th>
            <th>Status</th>
            <th>Last serviced</th>
          </tr>
        </thead>
        <tbody>
          {items.map((m) => (
            <tr key={m.id} onClick={() => open(m.id)}>
              <td>{m.asset_tag}</td>
              <td>{m.name}</td>
              <td>{m.city}</td>
              <td>{m.region}</td>
              <td>
                <StatusBadge status={m.status} />
              </td>
              <td>{formatDate(m.last_serviced_at)}</td>
            </tr>
          ))}
          {items.length === 0 && (
            <tr>
              <td colSpan={6} className="muted">
                No machines match these filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      <div className="pagination">
        <button
          className="secondary"
          disabled={offset === 0}
          onClick={() => setOffset(Math.max(0, offset - PAGE))}
        >
          ← Prev
        </button>
        <span>
          {total === 0 ? 0 : offset + 1}–{Math.min(offset + PAGE, total)} of{" "}
          {total.toLocaleString()}
        </span>
        <button
          className="secondary"
          disabled={offset + PAGE >= total}
          onClick={() => setOffset(offset + PAGE)}
        >
          Next →
        </button>
      </div>
    </div>
  );
}
