export type TrackedSatellite = {
  id: number;
  norad_id: number;
  name: string;
  is_tracked: boolean;
  updated_at: string;
};

export type PredictResponse = {
  satellite_id: number;
  latitude_deg: number;
  longitude_deg: number;
  altitude_km: number;
  timestamp_utc: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api/v1";

async function checkResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function fetchTrackedSatellites(): Promise<TrackedSatellite[]> {
  const response = await fetch(`${API_BASE}/satellites/tracked`);
  return checkResponse<TrackedSatellite[]>(response);
}

export async function fetchPrediction(satelliteId: number, atIso: string): Promise<PredictResponse> {
  const url = new URL(`${API_BASE}/predict/${satelliteId}`);
  url.searchParams.set("t", atIso);
  const response = await fetch(url.toString());
  return checkResponse<PredictResponse>(response);
}
