// Journey to the West: the novel has realms, not territories.
//
// The engine always gives a pack's periods the atlas's own world border maps (addPack in app.js), so with a
// chapter axis of 1-100 the Han empire of 1 CE and 100 CE would sit under the pilgrimage. This plugin switches
// those layers off and offers them back as one chip, so a reader can compare the novel's space with the real
// world of the 7th century if they want to.
//
// Everything else the novel needs (the road west, the kingdoms, the three realms, the four continents) is a
// plain GeoJSON layer in the manifest, drawn by the engine.

const BORDERS = ["neighbour-fill", "neighbour-line", "focus-fill", "focus-casing", "focus-line", "hl-fill", "hl-line"];

export default function setup(atlas) {
  let on = false;
  const apply = () => {
    for (const id of BORDERS) {
      if (atlas.map.getLayer(id)) atlas.map.setLayoutProperty(id, "visibility", on ? "visible" : "none");
    }
  };

  apply();
  atlas.addToggle({ id: "worldborders", name: "Real borders", name_zh: "真实疆域", on: false }, (v) => { on = v; apply(); });
  // The engine redraws borders when the year changes and the Neighbours chip flips its own two layers, so
  // re-assert the choice afterwards.
  atlas.on("year", apply);

  // "Neighbours" means nothing with no borders on the map; the chip above replaces it.
  document.getElementById("t-neighbours")?.setAttribute("hidden", "");
}
