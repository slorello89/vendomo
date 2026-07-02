import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { api } from "../api";
import type { Stats } from "../types";

export default function Header() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.stats().then(setStats).catch((e) => console.error(e));
  }, []);

  return (
    <header className="header">
      <div className="brand">
        <img src="/vendomo-mark-dark.svg" alt="" className="brand-mark" />
        <span>Vendomo</span>
      </div>
      <nav className="nav">
        <NavLink to="/" end>
          Map
        </NavLink>
        <NavLink to="/list">Machines</NavLink>
        <NavLink to="/ingest">Ingest</NavLink>
        <NavLink to="/service">Service</NavLink>
      </nav>
      <div className="header-stats">
        {stats && (
          <>
            <span>
              <strong>{stats.total_machines.toLocaleString()}</strong> machines
            </span>
            <span>
              <strong>{stats.needs_service.toLocaleString()}</strong> need service
            </span>
          </>
        )}
      </div>
    </header>
  );
}
