# Custom data: data packs

The atlas is an engine. It supplies the world map, terrain, satellite imagery, world borders from 3000 BCE to today,
the timeline, tours, search and the UI. **Your history** (periods, events, tours and map layers) lives in a **data
pack**: a folder of JSON files with a `manifest.json`, published on your own site. Point the atlas at it with `?pack=`:

```
https://atlas.daiyip.com/?pack=https://example.org/atlas/manifest.json
https://atlas.daiyip.com/?pack=https://example.org/atlas/manifest.json&packonly=1
```

- By default the pack is **added** to the atlas's own data. Its periods become one more region, which wins inside its
  outline, and its events and tours sit beside the built-in ones.
- With `packonly=1` the pack is **shown alone**. The atlas's own events, tours, cities, per-period layers and overlays
  are left out, and so are the layer switches and ledger tabs that would be empty.

A complete working pack is in [`examples/demo-pack/`](../examples/demo-pack/). It has one period, 61 events, Paul's
three journeys as tours, two map layers and a plugin.

## A minimal pack

```
my-pack/
  manifest.json
  eras.json
  events.json
  tours.json        (optional)
```

`manifest.json`:

```json
{
  "atlas": 1,
  "id": "rome",
  "name": "Ancient Rome",
  "name_zh": "古罗马",
  "region": {
    "polygon": [[-10, 35], [40, 35], [40, 55], [-10, 55]],
    "view": { "center": [12.5, 41.9], "zoom": 5, "year": -44 }
  },
  "range": { "start": -753, "end": 476 },
  "data": { "eras": "eras.json", "events": "events.json", "tours": "tours.json" },
  "attribution": "Events: my sources"
}
```

## Manifest

| Key | Meaning |
| --- | --- |
| `atlas` | Pack format version, `1`. The atlas refuses versions it doesn't know. |
| `id` | Lowercase letters, digits and `-`. It is also the region id, and the key the browser remembers the view under. |
| `name`, `name_zh` | Display name in English and Chinese. |
| `data.eras`, `data.events` | Required. Paths relative to the manifest. |
| `data.tours` | Optional guided tours. |
| `data.people` | Optional rulers and famous people (see [people.json](#peoplejson-rulers-and-people)). |
| `region.polygon` | Outline `[[lon, lat], ...]`. While the map is mostly inside it, the timeline shows the pack's periods. `region.bounds` (`[[west, south], [east, north]]`) is used as a box when there is no polygon. |
| `region.view` | First view when there is no link and no remembered view: `center`, `zoom`, `year`. |
| `range` | `{start, end}`: the years the pack's periods cover. Negative years are BCE. |
| `refs` | Optional link back to your own site. Events with `refs` and tour steps with `ref` get a link built from `url`, with `{ref}` replaced. `label` and `label_zh` are its tooltip. |
| `attribution` | Added to the map credits. |
| `note`, `note_zh` | When the pack is shown alone, this replaces the borders note in the side panel. |
| `layers` | Map overlays drawn from GeoJSON. See [plugins.md](plugins.md#layers). |
| `library` | Optional path to a shelf of packs to switch between (see [A shelf of packs](#a-shelf-of-packs)). |
| `plugins` | JavaScript modules that extend the atlas. See [plugins.md](plugins.md#plugins). |

Text fields come in pairs: `x` in English and `x_zh` in Chinese. If the Chinese one is missing, the English one is
shown.

## eras.json: the periods

```json
{
  "range": { "start": 31, "end": 100 },
  "eras": [
    { "id": "early-church", "name": "The Early Church", "name_zh": "初期教会", "glyph": "使徒",
      "short": "Early Church", "tiny": "Chr", "start": 31, "end": 100,
      "summary": "The apostles preach from Jerusalem to Rome.", "summary_zh": "使徒从耶路撒冷一直传道到罗马。" }
  ]
}
```

Periods must follow each other with no gaps. `glyph` is the seal in the era card (one or two characters). `short`
and `tiny` are the labels on the timeline when space runs out.

### Border maps

By default a pack's periods use the atlas's world border maps, so they need nothing more. A period can bring its own
maps instead, as `snapshots`, a list of GeoJSON files with the year each takes over:

```json
{ "id": "red-cliffs", "start": 208, "end": 210, "...": "...",
  "snapshots": [
    { "from": 208, "borders": "borders/sg-207.geojson", "label": "207: Cao Cao has united the north", "label_zh": "207年：曹操统一北方" },
    { "from": 209, "borders": "borders/sg-209.geojson" }
  ] }
```

Paths are relative to the manifest, and may point at the atlas's own maps on the same site
(`../../data/borders/eastern-han.geojson`). The maps are drawn like the atlas's dynasty maps: inside the East Asia
window, with the outer world map around it. Features take the shape of `data/borders/*.geojson`: `name`, `name_zh`, a
`label` point, `area`, optional `color`, and `focus: true` for the states the period is about (the rest are drawn as
neighbours). A period's `focus` list of names, if given, overrides the flags. `label` / `label_zh` describe the map in
the era card. The Three Kingdoms pack builds its maps from commandery seats with `tools/build_states.py`
(`tools/sanguo/build_borders.py`).

## events.json: dated, located events

```json
[
  { "id": "paul-at-athens", "year": 50, "level": 1, "category": "culture",
    "title": "Paul at Athens", "title_zh": "保罗在雅典",
    "place": "Athens", "place_zh": "雅典", "lat": 37.97, "lon": 23.72,
    "summary": "Paul speaks on the Areopagus.", "summary_zh": "保罗在亚略巴古讲道。",
    "refs": ["Acts.17.16-34"] }
]
```

| Field | Meaning |
| --- | --- |
| `id` | Unique across the pack. |
| `year`, `endYear` | When it happened (the end is optional). |
| `lat`, `lon` | Where. |
| `level` | `1` key, `2` major, `3` detail. The event filter and timeline zoom use it. |
| `category` | One of `war`, `politics`, `reform`, `rebellion`, `diplomacy`, `economy`, `culture`, `science`, `society`. |
| `title`, `place`, `summary` (+ `_zh`) | Text for the list, the map card and the story view. |
| `refs` | Optional, for the manifest's `refs` link. |
| `people` | Optional ids from `data.people`: the story shows them as chips, and each person's card lists their events. |

## tours.json: guided tours

```json
[
  { "id": "paul-first", "era": "early-church", "path": true,
    "title": "Paul's first journey", "title_zh": "保罗第一次旅行布道",
    "steps": [
      { "year": 45, "at": [36.165, 36.201], "zoom": 6.4, "event": "first-missionary-journey", "ref": "Acts.13.1-3",
        "text": "The church at Antioch sends them out.", "text_zh": "安提阿的教会差遣他们出去。" }
    ] }
]
```

Each step flies the camera to `at` (with optional `zoom`, `pitch` and `bearing`), moves the timeline to `year` and
shows `text`. `event` links the step to an event's story, and `path: true` draws the journey so far.

## people.json: rulers and people

The same three lists as the atlas's own per-period files (`data/layers/<era>.json`), for the whole pack; each period
gets the reigns and lives that touch its years. With them, a pack shown alone keeps the Rulers and People tabs and
their map switches, which it otherwise hides.

```json
{
  "polities": { "Wei": { "name_zh": "曹魏", "focus": true } },
  "rulers": { "Wei": [ { "name": "Cao Pi", "name_zh": "曹丕", "title": "Emperor Wen of Wei", "title_zh": "魏文帝", "from": 220, "to": 226 } ] },
  "people": [ { "id": "zhuge-liang", "name": "Zhuge Liang", "name_zh": "诸葛亮", "born": 181, "died": 234, "show": [207, 234],
                "field": "strategist", "place": "Longzhong", "place_zh": "隆中", "lat": 32.0, "lon": 112.05,
                "known_for": "...", "known_for_zh": "..." } ]
}
```

| Field | Meaning |
| --- | --- |
| `polities` | Countries by key: `name_zh`, and `focus` for the main ones (listed first). A key that is also a `name` on the period's border map puts the reigning ruler under that label. |
| `rulers` | Reigns by country key: `name`, `title` (+ `_zh`), `from`, `to`, optional `circa`. In a handover year the later reign wins. |
| `people` | `id`, `name`, `born`, `died`, `field` (`general`, `statesman`, `strategist`, `thinker`, `poet`, `writer`, `historian`, `scholar`, `religious`, `artist`, `scientist`, `physician`, `engineer`, `explorer` or `other`), `place`, `lat`, `lon`, `known_for` (+ `_zh`). The marker shows for the life, or for `show: [from, to]` when given; a person with no `died` needs `show`. |

## A shelf of packs

Several packs on one site can be switched between from the region chip at the top left. Each manifest names the same
library file, and the chip's menu lists its entries:

```json
{ "packs": [
  { "id": "xiyouji", "name": "Journey to the West", "name_zh": "西游记", "sub": "Chapters 1–100", "sub_zh": "第1–100回",
    "color": "#c47a2c", "manifest": "xiyouji/manifest.json" },
  { "id": "sanguo", "name": "Romance of the Three Kingdoms", "name_zh": "三国演义", "manifest": "sanguo/manifest.json" },
  { "id": "atlas", "name": "History atlas", "name_zh": "历代地图" }
] }
```

`manifest` paths are relative to the library file; an entry with no manifest opens the atlas itself. Picking an entry
reloads the page with that pack shown alone, in the current language, so each pack keeps its own timeline, layers
and plugins. The library and its packs follow the same allowlist as any pack. This repository's shelf is
`packs/index.json`.

## Hosting and the allowlist

Pack text is put into the atlas page, so the atlas only loads packs (and plugins) from a short list of sites:
`PACK_ORIGINS` at the top of `app.js`, plus the atlas's own site and `localhost` for development. Today the list is
`atlas.daiyip.com`, `bible.daiyip.com` and `daiyip.github.io`. You have two ways to use your own pack:

1. **Self-host the atlas.** It is a static site with no build step. Fork the repo, put your pack in a folder next to
   it (for example `packs/rome/`) and open `/?pack=packs/rome/manifest.json`. A pack on the same site always loads.
2. **Use atlas.daiyip.com.** Open a pull request that adds your site to `PACK_ORIGINS`. Your pack's files must be served
   with `Access-Control-Allow-Origin` (GitHub Pages does this for you).

To try a pack while you write it, serve the atlas and your pack locally:

```sh
python3 -m http.server 8000          # from the atlas checkout
# open http://localhost:8000/?pack=examples/demo-pack/manifest.json&packonly=1
```

## Links into a pack

The address keeps the view, so you can link straight to a moment:

| Hash key | Meaning |
| --- | --- |
| `y` | Year, for example `y=-44`. |
| `c` | Camera: `lon,lat,zoom,pitch,bearing`. |
| `e` | Open this event's story. |
| `tour`, `s` | Start this tour at step `s` (counting from 1). |
| `l=en` | English. |

For example: `/?pack=…/manifest.json&packonly=1#tour=paul-first&s=3&l=en`. Changing the hash reloads the atlas at the
new place. This is how a host page moves an embedded atlas (see the README).
