import { useMemo } from "react";
import type { IncidentSummary } from "../../lib/types";

/**
 * SVG threat map that plots incidents on an equirectangular world projection.
 * Purely offline: no Google Maps key required. Arcs are drawn from the
 * incident origin to every other incident in the same propagation chain
 * (map_region values containing "->").
 */

type Marker = {
  id: string;
  severity: string;
  title: string;
  region: string;
  lat: number;
  lng: number;
};

type Arc = {
  key: string;
  from: { x: number; y: number };
  to: { x: number; y: number };
};

const VIEW_W = 1000;
const VIEW_H = 500;

function project(lat: number, lng: number): { x: number; y: number } {
  const x = ((lng + 180) / 360) * VIEW_W;
  const y = ((90 - lat) / 180) * VIEW_H;
  return { x, y };
}

const CITY_COORDS: Record<string, [number, number]> = {
  singapore: [1.3521, 103.8198],
  london: [51.5074, -0.1278],
  dubai: [25.2048, 55.2708],
  bengaluru: [12.9716, 77.5946],
  bangalore: [12.9716, 77.5946],
  berlin: [52.52, 13.405],
  cairo: [30.0444, 31.2357],
  nairobi: [-1.2921, 36.8219],
  lisbon: [38.7223, -9.1393],
  "são paulo": [-23.5505, -46.6333],
  "sao paulo": [-23.5505, -46.6333],
  seoul: [37.5665, 126.978],
  tokyo: [35.6762, 139.6503],
  jakarta: [-6.2088, 106.8456],
  manila: [14.5995, 120.9842],
  mumbai: [19.076, 72.8777],
  delhi: [28.6139, 77.209],
  "new york": [40.7128, -74.006],
  "los angeles": [34.0522, -118.2437],
  paris: [48.8566, 2.3522],
  madrid: [40.4168, -3.7038],
  sydney: [-33.8688, 151.2093],
};

function chainCities(region: string | undefined): [number, number][] {
  if (!region) return [];
  const parts = region
    .replace(/→/g, "->")
    .split("->")
    .map((p) => p.trim().toLowerCase());
  const coords: [number, number][] = [];
  for (const p of parts) {
    if (CITY_COORDS[p]) coords.push(CITY_COORDS[p]);
  }
  return coords;
}

function severityStops(severity: string): { fill: string; ring: string } {
  const s = (severity || "").toLowerCase();
  if (s === "strike") return { fill: "#ff4f6b", ring: "rgba(255,79,107,0.35)" };
  if (s === "verified") return { fill: "#49d17a", ring: "rgba(73,209,122,0.35)" };
  return { fill: "#78b4ff", ring: "rgba(120,180,255,0.35)" };
}

export type ThreatMapProps = {
  incidents: IncidentSummary[];
  freshIds?: Set<string>;
  height?: number;
  onSelect?: (incidentId: string) => void;
};

export function ThreatMap({ incidents, freshIds, height = 320, onSelect }: ThreatMapProps) {
  const { markers, arcs } = useMemo(() => {
    const markers: Marker[] = [];
    const arcs: Arc[] = [];
    for (const inc of incidents) {
      const lat = inc.map_lat ?? null;
      const lng = inc.map_lng ?? null;
      if (typeof lat === "number" && typeof lng === "number") {
        markers.push({
          id: inc.incident_id,
          severity: inc.severity,
          title: inc.title,
          region: inc.region || "",
          lat,
          lng,
        });
      }
      const chain = chainCities(inc.region);
      for (let i = 0; i < chain.length - 1; i += 1) {
        const [aLat, aLng] = chain[i];
        const [bLat, bLng] = chain[i + 1];
        arcs.push({
          key: `${inc.incident_id}-${i}`,
          from: project(aLat, aLng),
          to: project(bLat, bLng),
        });
      }
    }
    return { markers, arcs };
  }, [incidents]);

  const hasData = markers.length > 0 || arcs.length > 0;

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height,
        borderRadius: 14,
        overflow: "hidden",
        background:
          "radial-gradient(1200px 500px at 30% 20%, rgba(80,110,180,0.35), transparent 60%), " +
          "radial-gradient(900px 500px at 80% 80%, rgba(180,80,140,0.25), transparent 60%), " +
          "linear-gradient(180deg, #0b1026 0%, #050616 100%)",
        boxShadow: "inset 0 0 80px rgba(0,0,0,0.55)",
      }}
    >
      <svg
        viewBox={`0 0 ${VIEW_W} ${VIEW_H}`}
        preserveAspectRatio="xMidYMid meet"
        style={{ width: "100%", height: "100%", display: "block" }}
      >
        <defs>
          <linearGradient id="arcGradient" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="rgba(120,180,255,0.05)" />
            <stop offset="50%" stopColor="rgba(120,180,255,0.85)" />
            <stop offset="100%" stopColor="rgba(255,79,107,0.9)" />
          </linearGradient>
          <radialGradient id="markerHalo" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(255,255,255,0.9)" />
            <stop offset="100%" stopColor="rgba(255,255,255,0)" />
          </radialGradient>
        </defs>

        {/* Longitude grid */}
        {Array.from({ length: 13 }).map((_, i) => {
          const x = (i * VIEW_W) / 12;
          return (
            <line
              key={`lng-${i}`}
              x1={x}
              y1={0}
              x2={x}
              y2={VIEW_H}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth={1}
            />
          );
        })}
        {/* Latitude grid */}
        {Array.from({ length: 7 }).map((_, i) => {
          const y = (i * VIEW_H) / 6;
          return (
            <line
              key={`lat-${i}`}
              x1={0}
              y1={y}
              x2={VIEW_W}
              y2={y}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth={1}
            />
          );
        })}

        {/* Simple continent silhouettes (polygon blobs, decorative) */}
        <g fill="rgba(120,150,200,0.10)" stroke="rgba(120,150,200,0.22)" strokeWidth={0.6}>
          {/* North America */}
          <path d="M 120 100 Q 180 70 260 100 Q 310 140 260 210 Q 200 240 150 210 Q 100 170 120 100 Z" />
          {/* South America */}
          <path d="M 280 240 Q 330 220 340 280 Q 330 360 290 400 Q 260 380 270 320 Q 260 270 280 240 Z" />
          {/* Europe */}
          <path d="M 490 100 Q 560 80 580 130 Q 560 170 510 170 Q 470 150 490 100 Z" />
          {/* Africa */}
          <path d="M 500 190 Q 570 180 590 240 Q 580 320 530 360 Q 490 330 490 260 Q 480 210 500 190 Z" />
          {/* Asia */}
          <path d="M 600 90 Q 740 70 830 130 Q 850 200 760 230 Q 680 220 620 200 Q 580 150 600 90 Z" />
          {/* Oceania */}
          <path d="M 810 330 Q 870 320 880 360 Q 860 390 810 380 Q 790 360 810 330 Z" />
          {/* India peninsula */}
          <path d="M 670 190 Q 700 200 700 250 Q 680 270 660 240 Q 650 210 670 190 Z" />
        </g>

        {/* Propagation arcs */}
        {arcs.map((arc) => {
          const midX = (arc.from.x + arc.to.x) / 2;
          const midY = (arc.from.y + arc.to.y) / 2 - Math.abs(arc.to.x - arc.from.x) * 0.25;
          return (
            <g key={arc.key}>
              <path
                d={`M ${arc.from.x} ${arc.from.y} Q ${midX} ${midY} ${arc.to.x} ${arc.to.y}`}
                fill="none"
                stroke="url(#arcGradient)"
                strokeWidth={1.4}
                strokeLinecap="round"
                strokeDasharray="4 6"
                opacity={0.85}
              >
                <animate
                  attributeName="stroke-dashoffset"
                  from="0"
                  to="-40"
                  dur="3s"
                  repeatCount="indefinite"
                />
              </path>
            </g>
          );
        })}

        {/* Incident markers */}
        {markers.map((m) => {
          const { x, y } = project(m.lat, m.lng);
          const isFresh = freshIds?.has(m.id);
          const colors = severityStops(m.severity);
          return (
            <g
              key={m.id}
              style={{ cursor: onSelect ? "pointer" : "default" }}
              onClick={() => onSelect?.(m.id)}
            >
              <title>{`${m.id} — ${m.title}\n${m.region}`}</title>
              <circle cx={x} cy={y} r={14} fill={colors.ring} opacity={0.7}>
                {isFresh && (
                  <animate
                    attributeName="r"
                    values="10;22;10"
                    dur="1.8s"
                    repeatCount="indefinite"
                  />
                )}
              </circle>
              <circle cx={x} cy={y} r={5} fill={colors.fill} stroke="#ffffff" strokeWidth={1.2} />
            </g>
          );
        })}
      </svg>

      {/* Legend / empty state */}
      <div
        style={{
          position: "absolute",
          left: 14,
          top: 14,
          padding: "6px 10px",
          borderRadius: 8,
          background: "rgba(6,10,25,0.7)",
          backdropFilter: "blur(6px)",
          fontSize: 11,
          color: "rgba(255,255,255,0.85)",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#ff4f6b",
              boxShadow: "0 0 6px #ff4f6b",
            }}
          />
          Strike
        </span>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#78b4ff",
              boxShadow: "0 0 6px #78b4ff",
            }}
          />
          Monitor
        </span>
        <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#49d17a",
              boxShadow: "0 0 6px #49d17a",
            }}
          />
          Verified
        </span>
      </div>
      <div
        style={{
          position: "absolute",
          right: 14,
          top: 14,
          padding: "6px 10px",
          borderRadius: 8,
          background: "rgba(6,10,25,0.7)",
          backdropFilter: "blur(6px)",
          fontSize: 11,
          color: "rgba(255,255,255,0.85)",
        }}
      >
        {markers.length} geolocated · {arcs.length} propagation edges
      </div>
      {!hasData && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "rgba(255,255,255,0.55)",
            fontSize: 13,
            letterSpacing: 0.3,
          }}
        >
          No geolocated incidents yet — seed the scenario or simulate from Settings.
        </div>
      )}
    </div>
  );
}
