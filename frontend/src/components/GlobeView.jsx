import { useEffect, useRef } from "react";
import Globe from "globe.gl";

function confidenceColor(score) {
  if (score >= 90) return "#FF3B3B";
  if (score >= 80) return "#FF8C00";
  return "#FFD700";
}

export default function GlobeView({ arcs }) {
  const mountRef = useRef(null);
  const globeRef = useRef(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const globe = Globe()(mountRef.current)
      .globeImageUrl("//unpkg.com/three-globe/example/img/earth-night.jpg")
      .backgroundImageUrl("//unpkg.com/three-globe/example/img/night-sky.png")
      .width(mountRef.current.clientWidth)
      .height(mountRef.current.clientHeight)
      .arcsData([])
      .arcStartLat((d) => d.src_lat)
      .arcStartLng((d) => d.src_lon)
      .arcEndLat((d) => d.dst_lat)
      .arcEndLng((d) => d.dst_lon)
      .arcColor((d) => [confidenceColor(d.confidence), "rgba(255,255,255,0.1)"])
      .arcAltitudeAutoScale(0.4)
      .arcStroke((d) => (d.confidence >= 90 ? 0.8 : 0.4))
      .arcDashLength(0.4)
      .arcDashGap(0.2)
      .arcDashAnimateTime(2000)
      .arcLabel(
        (d) =>
          `<div style="background:#0f172a;border:1px solid #334155;padding:6px 10px;border-radius:6px;font-family:monospace;font-size:12px;color:#e2e8f0">
            <b style="color:${confidenceColor(d.confidence)}">${d.ip}</b><br/>
            ${d.src_city}, ${d.src_country}<br/>
            Confidence: <b>${d.confidence}%</b>
          </div>`
      )
      .ringsData([])
      .ringLat((d) => d.src_lat)
      .ringLng((d) => d.src_lon)
      .ringColor((d) => confidenceColor(d.confidence))
      .ringMaxRadius(3)
      .ringPropagationSpeed(2)
      .ringRepeatPeriod(1000)
      .enablePointerInteraction(true);

    globe.controls().autoRotate = true;
    globe.controls().autoRotateSpeed = 0.4;
    globeRef.current = globe;

    const handleResize = () => {
      if (mountRef.current) {
        globe.width(mountRef.current.clientWidth);
        globe.height(mountRef.current.clientHeight);
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    if (!globeRef.current || !arcs.length) return;
    globeRef.current.arcsData(arcs);
    globeRef.current.ringsData(arcs);
  }, [arcs]);

  return <div ref={mountRef} style={{ width: "100%", height: "100%" }} />;
}