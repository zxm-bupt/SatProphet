import { useEffect, useRef } from "react";

import type { PredictResponse } from "../api/client";

type CesiumViewerProps = {
  prediction: PredictResponse | null;
  satelliteName: string;
};

export function CesiumViewer({ prediction, satelliteName }: CesiumViewerProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const viewerRef = useRef<any>(null);

  useEffect(() => {
    let disposed = false;

    void (async () => {
      if (!containerRef.current) {
        return;
      }

      try {
        const Cesium = await import("cesium");
        await import("cesium/Build/Cesium/Widgets/widgets.css");

        if (disposed || !containerRef.current) {
          return;
        }

        viewerRef.current = new Cesium.Viewer(containerRef.current, {
          animation: false,
          timeline: false,
          baseLayerPicker: false,
          geocoder: false,
          homeButton: false,
          sceneModePicker: false,
          navigationHelpButton: false,
        });
      } catch {
        if (containerRef.current) {
          containerRef.current.innerText = "Cesium 初始化失败，请先安装前端依赖并启动 dev server。";
        }
      }
    })();

    return () => {
      disposed = true;
      if (viewerRef.current) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    void (async () => {
      if (!prediction || !viewerRef.current) {
        return;
      }

      const Cesium = await import("cesium");
      const viewer = viewerRef.current;
      viewer.entities.removeAll();

      const point = Cesium.Cartesian3.fromDegrees(
        prediction.longitude_deg,
        prediction.latitude_deg,
        prediction.altitude_km * 1000,
      );

      viewer.entities.add({
        id: "satellite-point",
        name: satelliteName || `Satellite ${prediction.satellite_id}`,
        position: point,
        point: {
          pixelSize: 10,
          color: Cesium.Color.CYAN,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 1,
        },
        label: {
          text: satelliteName || `ID ${prediction.satellite_id}`,
          pixelOffset: new Cesium.Cartesian2(0, -18),
        },
      });

      viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(
          prediction.longitude_deg,
          prediction.latitude_deg,
          1_500_000,
        ),
      });
    })();
  }, [prediction, satelliteName]);

  return <div className="viewer-canvas" ref={containerRef} />;
}
