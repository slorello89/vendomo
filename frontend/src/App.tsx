import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import MapView from "./components/MapView";
import ListView from "./components/ListView";
import IngestionPanel from "./components/IngestionPanel";
import ServiceDashboard from "./components/ServiceDashboard";
import MachineDetailDrawer from "./components/MachineDetailDrawer";
import { SelectionContext } from "./context";

export default function App() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <SelectionContext.Provider value={{ open: setSelectedId }}>
      <div className="app">
        <Header />
        <main className="content">
          <Routes>
            <Route path="/" element={<MapView />} />
            <Route path="/list" element={<ListView />} />
            <Route path="/ingest" element={<IngestionPanel />} />
            <Route path="/service" element={<ServiceDashboard />} />
          </Routes>
        </main>
        <MachineDetailDrawer
          machineId={selectedId}
          onClose={() => setSelectedId(null)}
        />
      </div>
    </SelectionContext.Provider>
  );
}
