export type Metric = {
  label: string;
  value: string;
  delta: string;
};

export type Incident = {
  id: string;
  title: string;
  severity: "Verified" | "Monitor" | "Strike";
  platform: string;
  matchedAsset: string;
  confidence: string;
  spread: string;
  region: string;
  summary: string;
};

export type Asset = {
  id: string;
  title: string;
  type: "Image" | "Video" | "Live Watch";
  event: string;
  status: "Protected" | "Processing" | "Watching";
  provenance: "Verified" | "Present" | "Pending";
  incidents: number;
};

export type Segment = {
  minute: string;
  source: string;
  status: "Segment clean" | "Signal match" | "Restream suspected";
  latency: string;
};

export const overviewMetrics: Metric[] = [
  { label: "Active incidents", value: "14", delta: "+3 in 18m" },
  { label: "Protected assets", value: "126", delta: "48 video / 78 image" },
  { label: "Detection latency", value: "43s", delta: "-12s vs yesterday" },
  { label: "Live watch alerts", value: "4", delta: "1 high-priority relay" }
];

export const incidents: Incident[] = [
  {
    id: "INC-1042",
    title: "Championship highlight repost detected",
    severity: "Strike",
    platform: "YouTube mirror",
    matchedAsset: "Final whistle broadcast clip",
    confidence: "97.8%",
    spread: "High spread",
    region: "Singapore -> London -> Dubai",
    summary: "Credential missing, keyframes align with the protected highlight and repost velocity is accelerating."
  },
  {
    id: "INC-1037",
    title: "Edited sideline image circulating",
    severity: "Monitor",
    platform: "Reddit thread",
    matchedAsset: "Official trophy lift image",
    confidence: "89.2%",
    spread: "Moderate spread",
    region: "Bengaluru -> Berlin",
    summary: "Text overlay and crop detected, but visual structure remains strongly aligned to the official release."
  },
  {
    id: "INC-1030",
    title: "Fan meme built from official frame",
    severity: "Verified",
    platform: "Fan short-video feed",
    matchedAsset: "Celebration tunnel frame",
    confidence: "81.5%",
    spread: "Low spread",
    region: "Mumbai",
    summary: "Short humorous derivative with commentary context. Logged for visibility but unlikely to require escalation."
  }
];

export const assets: Asset[] = [
  {
    id: "AST-201",
    title: "Final whistle broadcast clip",
    type: "Video",
    event: "Championship Night",
    status: "Protected",
    provenance: "Verified",
    incidents: 7
  },
  {
    id: "AST-188",
    title: "Official trophy lift image",
    type: "Image",
    event: "Championship Night",
    status: "Protected",
    provenance: "Present",
    incidents: 4
  },
  {
    id: "AST-172",
    title: "Live tunnel cam watch",
    type: "Live Watch",
    event: "Semifinal Stream",
    status: "Watching",
    provenance: "Pending",
    incidents: 3
  }
];

export const liveSegments: Segment[] = [
  { minute: "74:18", source: "Primary feed A", status: "Segment clean", latency: "31s" },
  { minute: "74:24", source: "Short relay node", status: "Signal match", latency: "44s" },
  { minute: "74:31", source: "Mirror ingest", status: "Restream suspected", latency: "52s" }
];

export const evidencePoints = [
  "Protected video and monitored upload share the same end-frame choreography and scoreboard geometry.",
  "The suspicious upload has no embedded trust record while the official asset remains verified.",
  "Propagation velocity increased after the second repost source appeared.",
  "Action recommendation is escalation because confidence and spread are both high."
];
