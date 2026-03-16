import { create } from 'zustand';

interface EnergyState {
  solar_kw: number;
  consumption_kw: number;
  net_grid_kw: number;
  source: string;
  timestamp: string | null;
  setReading: (reading: Partial<EnergyState>) => void;
}

export const useEnergyStore = create<EnergyState>((set) => ({
  solar_kw: 0.0,
  consumption_kw: 0.0,
  net_grid_kw: 0.0,
  source: 'offline',
  timestamp: null,
  setReading: (reading) => set((state) => ({ ...state, ...reading })),
}));

interface AuthState {
  accessToken: string | null;
  isAuthenticated: boolean;
  user: any | null;
  setAuth: (token: string, user: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  isAuthenticated: false,
  user: null,
  setAuth: (token, user) => set({ accessToken: token, user, isAuthenticated: true }),
  logout: set({ accessToken: null, user: null, isAuthenticated: false }),
}));

interface ForecastState {
  forecast: any[];
  greenWindow: any | null;
  setForecast: (data: any[]) => void;
  setGreenWindow: (data: any) => void;
}

export const useForecastStore = create<ForecastState>((set) => ({
  forecast: [],
  greenWindow: null,
  setForecast: (forecast) => set({ forecast }),
  setGreenWindow: (greenWindow) => set({ greenWindow }),
}));
