// Romance of the Three Kingdoms: army movements, with direction arrows, marched out on tour steps.
//
// The routes are layers/campaigns.geojson (built by tools/sanguo/build_layers.py): one LineString or MultiLineString
// per march, in the direction of march, with from/to years and a colour per side. The engine draws the lines and
// filters them by year like any pack layer. This plugin adds what a pack layer cannot: arrowheads along each line, and,
// when a tour step names "route": ["id", ...], an animation of those routes being marched, over the same 2.6 seconds
// the camera takes to fly there, leaving a bright trail until the next step. One switch, 行军路线, controls all three.

const EMPTY = { type: "FeatureCollection", features: [] };
const MARCH_MS = 2600;

export default async function setup(atlas) {
  const map = atlas.map;
  const data = await atlas.fetchJSON("../layers/campaigns.geojson");
  const byId = new Map(data.features.map((f) => [f.properties.id, f]));
  const lines = atlas.addLayer({ id: "campaigns", chip: false, type: "line", color: "#8a8a5a", width: 3.5, data });
  const before = map.getLayer("tour-path") ? "tour-path" : undefined;
  // A pale casing under the lines, so they read on satellite imagery as well as on the relief map.
  map.addLayer({ id: "campaign-casing", type: "line", source: "pk-campaigns", layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": "#fff8ee", "line-width": 6.5, "line-opacity": 0.55 } }, lines.layerIds[0]);

  // An arrowhead, drawn once as a signed-distance image so each route can colour it.
  const S = 32, canvas = document.createElement("canvas");
  canvas.width = canvas.height = S;
  const g = canvas.getContext("2d");
  g.beginPath(); g.moveTo(7, 6); g.lineTo(27, 16); g.lineTo(7, 26); g.lineTo(13, 16); g.closePath(); g.fill();
  map.addImage("campaign-arrow", g.getImageData(0, 0, S, S), { sdf: true });
  map.addLayer({ id: "campaign-arrows", type: "symbol", source: "pk-campaigns",
    layout: { "symbol-placement": "line", "symbol-spacing": 90, "icon-image": "campaign-arrow", "icon-size": 0.85,
              "icon-allow-overlap": true, "icon-ignore-placement": true, "icon-rotation-alignment": "map" },
    paint: { "icon-color": ["get", "color"], "icon-halo-color": "#fff8ee", "icon-halo-width": 1.2 } }, before);

  // The march: a growing trail and a head.
  map.addSource("campaign-trail", { type: "geojson", data: EMPTY });
  map.addSource("campaign-head", { type: "geojson", data: EMPTY });
  map.addLayer({ id: "campaign-trail", type: "line", source: "campaign-trail", layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": ["get", "color"], "line-width": 6, "line-opacity": 0.85 } }, before);
  map.addLayer({ id: "campaign-head", type: "circle", source: "campaign-head",
    paint: { "circle-color": ["get", "color"], "circle-radius": 7, "circle-stroke-color": "#fff8ee", "circle-stroke-width": 2 } }, before);

  let on = true, frame = 0;
  const inYears = (y) => ["all", ["<=", ["coalesce", ["get", "from"], -1e6], y], [">", ["coalesce", ["get", "to"], 1e6], y]];
  const sync = () => {
    for (const id of ["campaign-casing", "campaign-arrows"]) {
      map.setFilter(id, inYears(atlas.year));
      map.setLayoutProperty(id, "visibility", on ? "visible" : "none");
    }
  };
  const clear = () => {
    cancelAnimationFrame(frame);
    map.getSource("campaign-trail").setData(EMPTY);
    map.getSource("campaign-head").setData(EMPTY);
  };
  atlas.addToggle({ id: "campaigns-switch", name: "Army movements", name_zh: "行军路线" }, (v) => {
    on = v;
    lines.show(v);
    sync();
    if (!v) clear();
  });
  atlas.on("year", sync);
  sync();

  // Each part of a route, with the running length along it, so a fraction of the march maps to a point.
  const parts = (f) => (f.geometry.type === "LineString" ? [f.geometry.coordinates] : f.geometry.coordinates).map((pts) => {
    const acc = [0];
    for (let i = 1; i < pts.length; i++) acc.push(acc[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
    return { pts, acc, len: acc[acc.length - 1] };
  });
  const cut = ({ pts, acc, len }, t) => {
    const d = len * t, out = [pts[0]];
    for (let i = 1; i < pts.length; i++) {
      if (acc[i] <= d) { out.push(pts[i]); continue; }
      const k = (d - acc[i - 1]) / (acc[i] - acc[i - 1] || 1);
      out.push([pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * k, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * k]);
      break;
    }
    return out;
  };

  function march(features) {
    const routes = features.map((f) => ({ color: f.properties.color, parts: parts(f) }));
    const t0 = performance.now();
    const step = (now) => {
      const t = Math.min(1, (now - t0) / MARCH_MS), ease = 1 - (1 - t) ** 2;
      const trail = [], heads = [];
      for (const r of routes) for (const p of r.parts) {
        const c = cut(p, ease);
        trail.push({ type: "Feature", properties: { color: r.color }, geometry: { type: "LineString", coordinates: c.length > 1 ? c : [c[0], c[0]] } });
        if (t < 1) heads.push({ type: "Feature", properties: { color: r.color }, geometry: { type: "Point", coordinates: c[c.length - 1] } });
      }
      map.getSource("campaign-trail").setData({ type: "FeatureCollection", features: trail });
      map.getSource("campaign-head").setData({ type: "FeatureCollection", features: heads });
      if (t < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
  }

  atlas.on("tour-step", ({ step }) => {
    clear();
    const features = [].concat(step.route || []).map((id) => byId.get(id)).filter(Boolean);
    if (on && features.length) march(features);
  });
  atlas.on("tour-end", clear);
}
