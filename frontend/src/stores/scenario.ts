import { create } from 'zustand'

interface ScenarioState {
  compliance: number
  awarenessBoost: number
  pickupFrequency: number
  binsPerStream: number
  facilityYieldOverride: Record<string, number>
  setCompliance: (v: number) => void
  setAwarenessBoost: (v: number) => void
  setPickupFrequency: (v: number) => void
  setBinsPerStream: (v: number) => void
  setFacilityYieldOverride: (v: Record<string, number>) => void
  reset: () => void
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  compliance: 0.6,
  awarenessBoost: 0,
  pickupFrequency: 1,
  binsPerStream: 1,
  facilityYieldOverride: {},
  setCompliance: (compliance) => set({ compliance }),
  setAwarenessBoost: (awarenessBoost) => set({ awarenessBoost }),
  setPickupFrequency: (pickupFrequency) => set({ pickupFrequency }),
  setBinsPerStream: (binsPerStream) => set({ binsPerStream }),
  setFacilityYieldOverride: (facilityYieldOverride) => set({ facilityYieldOverride }),
  reset: () => set({
    compliance: 0.6,
    awarenessBoost: 0,
    pickupFrequency: 1,
    binsPerStream: 1,
    facilityYieldOverride: {},
  }),
}))