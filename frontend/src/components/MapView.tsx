import { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import { api } from "../api";
import type { MapMarker } from "../types";
import { statusColor } from "../util";
import { useSelection } from "../context";

export default function MapView() {
  const [markers, setMarkers] = useState<MapMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const { open } = useSelection();

  useEffect(() => {
    setLoading(true);
    api
      .mapMarkers()
      .then(setMarkers)
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="map-wrap">
      <div className="map-overlay">
        {loading
          ? "Loading map…"
          : `Showing ${markers.length.toLocaleString()} machines`}
      </div>

      <MapContainer
        center={[39.5, -98.35]}
        zoom={4}
        className="map"
        preferCanvas
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((m) => (
          <CircleMarker
            key={m.id}
            center={[m.lat, m.lng]}
            radius={6}
            pathOptions={{
              color: statusColor(m.status),
              fillColor: statusColor(m.status),
              fillOpacity: 0.85,
              weight: 1,
            }}
            eventHandlers={{ click: () => open(m.id) }}
          >
            <Popup>
              <strong>{m.name}</strong>
              <br />
              {m.label}
              <br />
              <button onClick={() => open(m.id)}>View details</button>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      <div className="legend">
        <span>
          <span className="dot" style={{ background: statusColor("operational") }} />
          Operational
        </span>
        <span>
          <span className="dot" style={{ background: statusColor("needs_service") }} />
          Needs service
        </span>
        <span>
          <span className="dot" style={{ background: statusColor("offline") }} />
          Offline
        </span>
      </div>
    </div>
  );
}
