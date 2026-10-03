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
// The border maps also bring HTML labels with each polity's name (.mk-polity) and a line in the period card
// naming the map (#era-snap, "map: the world around 1 BCE"). Both describe a map the reader cannot see, so they
// go with it. Hidden labels have no width, and declutter() skips those, so they don't push other labels away.
const CSS = "html.xyj-no-borders .mk-polity, html.xyj-no-borders #era-snap { display: none !important; }";

export default function setup(atlas) {
  let on = false;
  const style = document.createElement("style");
  style.textContent = CSS;
  document.head.append(style);
  const apply = () => {
    for (const id of BORDERS) {
      if (atlas.map.getLayer(id)) atlas.map.setLayoutProperty(id, "visibility", on ? "visible" : "none");
    }
    document.documentElement.classList.toggle("xyj-no-borders", !on);
  };

  apply();
  atlas.addToggle({ id: "worldborders", name: "Real borders", name_zh: "真实疆域", on: false }, (v) => { on = v; apply(); });
  // The engine redraws borders when the year changes and the Neighbours chip flips its own two layers, so
  // re-assert the choice afterwards.
  atlas.on("year", apply);

  // "Neighbours" means nothing with no borders on the map; the chip above replaces it. In a pack shown alone it
  // is the last chip left in its group, so hide the group too, as init() does for groups it empties.
  const chip = document.getElementById("t-neighbours");
  if (chip) {
    chip.hidden = true;
    const group = chip.closest(".lg");
    if (group && ![...group.querySelectorAll(".chip")].some((c) => !c.hidden)) group.hidden = true;
  }
}
