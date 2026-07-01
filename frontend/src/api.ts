import type {
  Machine,
  MachineCreate,
  MachineDetail,
  MachineListResponse,
  MapMarker,
  ServiceLog,
  Stats,
} from "./types";

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return (await res.json()) as T;
}

function qs(params: Record<string, string | number | undefined>): string {
  const search = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== "") search.set(k, String(v));
  }
  const s = search.toString();
  return s ? `?${s}` : "";
}

export type MachineQuery = {
  limit?: number;
  offset?: number;
  status?: string;
  region?: string;
  q?: string;
};

export const api = {
  stats: () => http<Stats>("/stats"),

  mapMarkers: () => http<MapMarker[]>("/machines/map"),

  machines: (params: MachineQuery = {}) =>
    http<MachineListResponse>(`/machines${qs(params)}`),

  machine: (id: string) => http<MachineDetail>(`/machines/${id}`),

  createMachine: (body: MachineCreate) =>
    http<Machine>("/machines", { method: "POST", body: JSON.stringify(body) }),

  bulkCreate: (body: MachineCreate[]) =>
    http<{ created: number }>("/machines/bulk", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  serviceLogs: (params: { machine_id?: string; type?: string; limit?: number } = {}) =>
    http<ServiceLog[]>(`/service/logs${qs(params)}`),

  createServiceLog: (body: {
    machine_id: string;
    type: string;
    technician: string;
    notes: string;
  }) =>
    http<ServiceLog>("/service/logs", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
