export interface Machine {
  id: string;
  asset_tag: string;
  name: string;
  model: string;
  manufacturer: string;
  status: string;
  latitude: number;
  longitude: number;
  address: string;
  location_description: string | null;
  city: string;
  region: string;
  country: string;
  capacity: number;
  installed_at: string;
  last_serviced_at: string | null;
  created_at: string;
}

export interface MachineListResponse {
  items: Machine[];
  total: number;
  limit: number;
  offset: number;
}

export interface MapMarker {
  id: string;
  name: string;
  lat: number;
  lng: number;
  status: string;
  label: string;
}

export interface ServiceLog {
  id: string;
  machine_id: string;
  type: string;
  technician: string;
  notes: string;
  created_at: string;
}

export interface MachineDetail extends Machine {
  recent_service_logs: ServiceLog[];
}

export interface Stats {
  total_machines: number;
  by_status: Record<string, number>;
  by_region: Record<string, number>;
  needs_service: number;
  never_serviced: number;
}

export interface MachineCreate {
  name: string;
  model?: string;
  manufacturer?: string;
  status?: string;
  latitude: number;
  longitude: number;
  address?: string;
  location_description?: string;
  city: string;
  region: string;
  country?: string;
  capacity?: number;
}
