import { useEffect, useMemo, useState } from "react";

import { fetchPrediction, fetchTrackedSatellites, type PredictResponse, type TrackedSatellite } from "./api/client";
import { CesiumViewer } from "./viewer/CesiumViewer";


function toIsoLocalInput(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

export function App() {
  const [satellites, setSatellites] = useState<TrackedSatellite[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [predictAt, setPredictAt] = useState<string>(toIsoLocalInput(new Date()));
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    void (async () => {
      try {
        const data = await fetchTrackedSatellites();
        setSatellites(data);
        if (data.length > 0) {
          setSelectedId(data[0].id);
        }
      } catch (err) {
        const message = err instanceof Error ? err.message : String(err);
        setError(`加载卫星列表失败: ${message}`);
      }
    })();
  }, []);

  const selected = useMemo(
    () => satellites.find((item) => item.id === selectedId) ?? null,
    [satellites, selectedId],
  );

  const tleAgingWarning = useMemo(() => {
    if (!selected) {
      return "";
    }
    const updated = new Date(selected.updated_at).getTime();
    const ageMs = Date.now() - updated;
    const ageDays = ageMs / (24 * 60 * 60 * 1000);
    return ageDays > 3 ? "TLE 超过 3 天，预测精度可能下降" : "";
  }, [selected]);

  async function handlePredict(): Promise<void> {
    if (!selectedId) {
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await fetchPrediction(selectedId, new Date(predictAt).toISOString());
      setPrediction(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      setError(`预测请求失败: ${message}`);
      setPrediction(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="layout">
      <header className="header">
        <h1>SatProphet</h1>
        <p>Tracked satellites and on-demand geodetic prediction</p>
      </header>
      <section className="content">
        <aside className="panel">
          <h2>Tracked Satellites</h2>
          <select
            className="field"
            value={selectedId ?? ""}
            onChange={(event) => setSelectedId(Number(event.target.value))}
          >
            {satellites.length === 0 ? <option value="">No tracked satellites</option> : null}
            {satellites.map((sat) => (
              <option key={sat.id} value={sat.id}>
                {sat.name} ({sat.norad_id})
              </option>
            ))}
          </select>

          <label className="label" htmlFor="predictAt">
            Predict Time
          </label>
          <input
            id="predictAt"
            className="field"
            type="datetime-local"
            value={predictAt}
            onChange={(event) => setPredictAt(event.target.value)}
          />

          <button className="primary" onClick={() => void handlePredict()} disabled={loading || !selectedId}>
            {loading ? "Predicting..." : "Predict Position"}
          </button>

          {tleAgingWarning ? <p className="warning">{tleAgingWarning}</p> : null}
          {error ? <p className="error">{error}</p> : null}

          {prediction ? (
            <dl className="result">
              <dt>Latitude</dt>
              <dd>{prediction.latitude_deg.toFixed(4)}°</dd>
              <dt>Longitude</dt>
              <dd>{prediction.longitude_deg.toFixed(4)}°</dd>
              <dt>Altitude</dt>
              <dd>{prediction.altitude_km.toFixed(2)} km</dd>
              <dt>UTC</dt>
              <dd>{new Date(prediction.timestamp_utc).toISOString()}</dd>
            </dl>
          ) : null}
        </aside>

        <CesiumViewer prediction={prediction} satelliteName={selected?.name ?? ""} />
      </section>
    </main>
  );
}
