import { useState } from "react";
import { api } from "../api";
import type { MachineCreate } from "../types";

const SAMPLE_LOCATIONS: Array<Pick<MachineCreate, "city" | "region" | "latitude" | "longitude">> = [
  { city: "New York", region: "NY", latitude: 40.7128, longitude: -74.006 },
  { city: "Chicago", region: "IL", latitude: 41.8781, longitude: -87.6298 },
  { city: "Austin", region: "TX", latitude: 30.2672, longitude: -97.7431 },
  { city: "Seattle", region: "WA", latitude: 47.6062, longitude: -122.3321 },
  { city: "Miami", region: "FL", latitude: 25.7617, longitude: -80.1918 },
];

const EMPTY: MachineCreate = {
  name: "",
  model: "VendoMax 3000",
  manufacturer: "Vendomo",
  status: "operational",
  latitude: 0,
  longitude: 0,
  address: "",
  location_description: "",
  city: "",
  region: "",
  capacity: 40,
};

type Notice = { kind: "ok" | "err"; text: string } | null;

export default function IngestionPanel() {
  const [form, setForm] = useState<MachineCreate>(EMPTY);
  const [notice, setNotice] = useState<Notice>(null);
  const [bulk, setBulk] = useState("");
  const [bulkNotice, setBulkNotice] = useState<Notice>(null);

  const set = (patch: Partial<MachineCreate>) => setForm((f) => ({ ...f, ...patch }));

  const randomLocation = () => {
    const loc = SAMPLE_LOCATIONS[Math.floor(Math.random() * SAMPLE_LOCATIONS.length)];
    set({
      ...loc,
      latitude: +(loc.latitude + (Math.random() - 0.5) * 0.2).toFixed(6),
      longitude: +(loc.longitude + (Math.random() - 0.5) * 0.2).toFixed(6),
    });
  };

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setNotice(null);
    if (!form.name || !form.city || !form.region) {
      setNotice({ kind: "err", text: "Name, city and region are required." });
      return;
    }
    try {
      const created = await api.createMachine({
        ...form,
        latitude: Number(form.latitude),
        longitude: Number(form.longitude),
        capacity: Number(form.capacity),
      });
      setNotice({ kind: "ok", text: `Created ${created.asset_tag} — ${created.name}.` });
      setForm(EMPTY);
    } catch (err) {
      setNotice({ kind: "err", text: String(err) });
    }
  };

  const submitBulk = async () => {
    setBulkNotice(null);
    let parsed: MachineCreate[];
    try {
      parsed = JSON.parse(bulk);
      if (!Array.isArray(parsed)) throw new Error("Expected a JSON array of machines.");
    } catch (err) {
      setBulkNotice({ kind: "err", text: `Invalid JSON: ${String(err)}` });
      return;
    }
    try {
      const res = await api.bulkCreate(parsed);
      setBulkNotice({ kind: "ok", text: `Created ${res.created} machines.` });
      setBulk("");
    } catch (err) {
      setBulkNotice({ kind: "err", text: String(err) });
    }
  };

  return (
    <div className="page">
      <h1>Ingest machines</h1>

      <div className="columns">
        <div className="panel">
          <h2>Add a single machine</h2>
          {notice && <div className={`notice ${notice.kind}`}>{notice.text}</div>}
          <form className="form-grid" onSubmit={submit}>
            <div className="field full">
              <label>Name *</label>
              <input value={form.name} onChange={(e) => set({ name: e.target.value })} />
            </div>
            <div className="field">
              <label>City *</label>
              <input value={form.city} onChange={(e) => set({ city: e.target.value })} />
            </div>
            <div className="field">
              <label>Region (state) *</label>
              <input value={form.region} onChange={(e) => set({ region: e.target.value })} />
            </div>
            <div className="field">
              <label>Latitude *</label>
              <input
                type="number"
                step="any"
                value={form.latitude}
                onChange={(e) => set({ latitude: e.target.valueAsNumber })}
              />
            </div>
            <div className="field">
              <label>Longitude *</label>
              <input
                type="number"
                step="any"
                value={form.longitude}
                onChange={(e) => set({ longitude: e.target.valueAsNumber })}
              />
            </div>
            <div className="field">
              <label>Model</label>
              <input value={form.model} onChange={(e) => set({ model: e.target.value })} />
            </div>
            <div className="field">
              <label>Manufacturer</label>
              <input
                value={form.manufacturer}
                onChange={(e) => set({ manufacturer: e.target.value })}
              />
            </div>
            <div className="field">
              <label>Status</label>
              <select value={form.status} onChange={(e) => set({ status: e.target.value })}>
                <option value="operational">Operational</option>
                <option value="needs_service">Needs service</option>
                <option value="offline">Offline</option>
              </select>
            </div>
            <div className="field">
              <label>Capacity</label>
              <input
                type="number"
                value={form.capacity}
                onChange={(e) => set({ capacity: e.target.valueAsNumber })}
              />
            </div>
            <div className="field full">
              <label>Address</label>
              <input value={form.address} onChange={(e) => set({ address: e.target.value })} />
            </div>
            <div className="field full">
              <label>Location description</label>
              <input
                value={form.location_description}
                placeholder="e.g. In the back of the bowling alley by the pinball machines"
                onChange={(e) => set({ location_description: e.target.value })}
              />
            </div>
            <div className="field full" style={{ flexDirection: "row", gap: 10 }}>
              <button type="submit">Add machine</button>
              <button type="button" className="secondary" onClick={randomLocation}>
                Random US location
              </button>
            </div>
          </form>
        </div>

        <div className="panel">
          <h2>Bulk import (JSON)</h2>
          <p className="muted">
            Paste a JSON array of machines. Each needs at least <code>name</code>,{" "}
            <code>city</code>, <code>region</code>, <code>latitude</code>, <code>longitude</code>.
          </p>
          {bulkNotice && <div className={`notice ${bulkNotice.kind}`}>{bulkNotice.text}</div>}
          <textarea
            value={bulk}
            onChange={(e) => setBulk(e.target.value)}
            rows={16}
            style={{ width: "100%" }}
            placeholder={`[\n  {\n    "name": "Airport Terminal A #2 — Denver",\n    "city": "Denver",\n    "region": "CO",\n    "latitude": 39.8561,\n    "longitude": -104.6737,\n    "location_description": "Near gate B12 by the water fountain"\n  }\n]`}
          />
          <div style={{ marginTop: 10 }}>
            <button onClick={submitBulk} disabled={!bulk.trim()}>
              Import
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
