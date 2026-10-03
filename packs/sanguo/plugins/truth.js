// Romance of the Three Kingdoms: a coloured disc under each event marker saying how true the story is.
// Green: recorded history. Amber: a real event the novel embellished. Purple: the novel's invention.
//
// A plain GeoJSON layer cannot do this, because the engine shows an event's marker only while it is current,
// inside the current period, and passing the detail and topic filters; a static layer filtered by years would
// leave discs with no marker. So the discs are recomputed on every year change and filter click, with the same
// rules as isActive() and visibleEvents() in app.js. (In the decades zoom the engine narrows the window
// further; the discs follow the period there, which can show a few more.)

const TRUTH = {
  history: ["#2c7a68", "Recorded history", "正史有载"],
  embellished: ["#c9a227", "Real, but embellished by the novel", "史有其事，演义加工"],
  fiction: ["#8a4f9e", "The novel's invention", "小说虚构"],
};

export default async function setup(atlas) {
  const events = await atlas.fetchJSON("../events.json");
  const layer = atlas.addLayer({ id: "truth", name: "History or invention", name_zh: "正史·演义·虚构", type: "circle",
                                 color: TRUTH.history[0], radius: 15, data: { type: "FeatureCollection", features: [] } });
  // The engine's own filter row: the pressed detail level (1 key, 2 major, 3 all) and topic tags.
  const filter = () => document.getElementById("ev-filter");
  const detail = () => +(filter()?.querySelector("[data-lv][aria-pressed=true]")?.dataset.lv || 2);
  const cats = () => [...(filter()?.querySelectorAll("[data-cat][aria-pressed=true]") || [])].map((b) => b.dataset.cat).filter(Boolean);

  const update = () => {
    const era = atlas.era, y = atlas.year;
    if (!era) return;
    const span = Math.max(2, Math.round((era.end - era.start) / 60));
    const d = detail(), cs = cats();
    const features = events
      .filter((e) => e.year >= era.start && e.year <= era.end && y >= e.year && y <= (e.endYear ?? e.year + span)
        && (e.level || 1) <= d && (!cs.length || cs.includes(e.category)))
      .map((e) => {
        const [color, label, label_zh] = TRUTH[e.truth] || TRUTH.history;
        return { type: "Feature", geometry: { type: "Point", coordinates: [e.lon, e.lat] },
                 properties: { color, name: `${label}: ${e.title}`, name_zh: `${label_zh}：${e.title_zh}`,
                               text: `Chapter ${e.chapter}.`, text_zh: `第${e.chapter}回。` } };
      });
    layer.setData({ type: "FeatureCollection", features });
  };

  atlas.on("year", update);
  // Filter clicks rebuild the markers synchronously; recompute right after.
  filter()?.addEventListener("click", () => setTimeout(update, 0));
  update();
}
