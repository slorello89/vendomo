import { createContext, useContext } from "react";

interface Selection {
  open: (machineId: string) => void;
}

export const SelectionContext = createContext<Selection>({ open: () => {} });

export const useSelection = () => useContext(SelectionContext);
