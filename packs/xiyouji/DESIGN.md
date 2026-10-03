# Journey to the West as a data pack — design

A design for `packs/xiyouji/`, a pack that puts 《西游记》 (*Journey to the West*, 1592) on the atlas.

**What this is really testing.** The atlas was built for history: a year axis, territorial borders, dated events at
real coordinates. A novel breaks all three assumptions — it has chapters instead of years, realms instead of
borders, and places that are invented, half-real or in heaven. If the engine can carry 《西游记》 without being
rewritten, it can carry any narrative with a spatial trajectory, and the "history map" is really a *narrative*
map that happens to be used for history.

《西游记》 is the right test case because it is the hard case in a useful way: it has a solid real skeleton
(the monk 玄奘 Xuanzang really did walk from 长安 to India, 629–645) with a thick fictional overlay on top. So we
can measure the fiction against something the engine already handles — the atlas ships that journey as the
`xuanzang` tour in `data/tours.json`, 8 steps, with coordinates we can reuse.

## 1. Success criteria

The pack is a success if, with **no changes to `app.js`**, a reader can:

1. Drag the timeline from 第一回 to 第一百回 and watch the pilgrimage advance across the map.
2. Click any of the 八十一难 and read what happened there, with a link to the original chapter text.
3. Play a tour (孙悟空's rise and fall; 唐僧's road west) and have the camera fly the route.
4. Switch on layers for 取经路线, 人间国度, 四大部洲 and 三界.
5. See which episodes sit on a real place, which sit on a traditional identification, and which are invented.

Point 5 matters: the pack should be honest about its own geography rather than pretend the novel is a travelogue.

## 2. The three mismatches, and what we do about them

### 2.1 The axis: chapters, not years

The novel has no usable chronology. Internally it spans centuries (悟空 is pinned under 五行山 for five hundred
years) but the pilgrimage itself is "fourteen years" of undated travel. The only monotonic scale the book
actually offers is the **chapter number**.

The engine does not care what a "year" means — `state.year` is an integer, eras are back-to-back integer ranges,
and events sort by it. So:

> **Decision: one chapter = one unit on the axis. `range: { start: 1, end: 100 }`.**

The timeline becomes a progress bar through the book, which is also how a reader experiences it. Everything else
in the engine keeps working unchanged: the three timeline zooms, the event filter, the tick marks, the tours.

Cost: `fmtYear()` (`app.js:141`) will render the axis as `1年 … 100年` / `1 … 100 CE`. For the first pass we
accept that; §6 proposes a ~20-line generalization that makes it read 第一回 / Ch. 1.

The historical dates are not thrown away. Where the real journey touches an episode, the event's summary ends
with a `史实：` / `Historically:` clause (第二十二回 流沙河 ↔ the Mokhayan desert, 629). That comparison is the
point of the pack. *(As built: a quarter of the events, 33 of 134, carry one. See §10.)*

### 2.2 Space: realms, not borders

Pack eras always get their borders from the atlas's world maps — `addPack()` at `app.js:501-503` overwrites any
`snapshots` the pack supplies:

```js
const list = eras.eras.map((e) => ({ ...e, region: id, worldMaps: true,
  focus: e.focus || [], snapshots: worldSnaps(e.start, e.end) }));   // ...e comes first, so it loses
```

With a 1–100 axis, `worldSnaps(1, 100)` resolves to `data/world/-1.json` and `data/world/100.json` — the Han
empire would sit under the pilgrimage as a backdrop. Wrong, and distracting.

> **Decision: the pack hides the engine's border layers from a plugin, and draws its own space instead.**

A plugin gets the raw MapLibre map (`atlas.map`), so `plugins/realms.js` switches off `neighbour-fill`,
`neighbour-line`, `focus-fill`, `focus-casing`, `focus-line`, `hl-fill` and `hl-line` on startup, together with
the polity name labels and the period card's "map: the world around 1 BCE" line, and offers all of it back as
one 真实疆域 / Real borders chip. What replaces them is the novel's own geography, as pack layers:

| Layer | Type | What it is |
| --- | --- | --- |
| 四大部洲 | `fill` | Four symbolic continents: 东胜神洲, 南赡部洲, 西牛贺洲, 北俱芦洲. Deliberately vague blobs — the book is vague. |
| 取经路线 | `line` | The road west, derived from the events: each leg carries the `from` chapter it is reached in, so it grows as the timeline moves. |
| 人间国度 | `circle` | The ten kingdoms the pilgrims pass through, plus the Tang, each with a card, appearing on arrival. |
| 三界 | `circle` | 天宫, 地府, 龙宫, 灵山 — see below. |

### 2.3 Places: real, identified, or invented

Every event needs a `lat`/`lon`. Each place gets a `ground` field saying how we got it, and the reader can see it
two ways, so the map never lies about its own certainty: the pack's own layers colour each feature by footing
(the road's legs by where they arrive, the kingdoms by where they sit), and every uncertain `place_zh` carries
the doubt in a parenthetical, e.g. 车迟国（焉耆一带？）. Event markers themselves cannot be restyled: the engine
builds them and the plugin API has no hook for it.

| `ground` | Meaning | Examples |
| --- | --- | --- |
| `real` | Attested place, coordinates from the atlas's own data | 长安 `108.96, 34.22`; 玉门关 `95.8, 40.3`; 高昌 `89.5, 42.9`; 那烂陀 `85.44, 25.13`; 曲女城 `79.9, 27.06`; 于阗 `79.9, 37.1` (all reused from the `xuanzang` tour) |
| `identified` | Fictional name with a traditional real-world identification | 火焰山 → 吐鲁番 `89.2, 42.9`; 流沙河 → 莫贺延碛; 女儿国 → 《大唐西域记》东女国 `80.5, 31.5`; 车迟国 → 焉耆 `86.57, 42.06`; 通天河 → 青海通天河 `96.6, 33.4`; 花果山 → 连云港云台山 `119.4, 34.5` |
| `projected` | Mythic space, placed at the earthly site its cult belongs to | 地府 → 泰山 `117.1, 36.25` (泰山治鬼); 天宫 → 昆仑 `80, 36` (天柱); 龙宫 → 东海 `122.5, 31.0`; 灵山 → 灵鹫山 `85.45, 25.0`; 灵台方寸山 → 西牛贺洲, placed northwest of India `73, 34` |
| `invented` | No defensible anchor; placed on the route by interpolation | most of the 妖怪 lairs between kingdoms |

The `projected` row is the interesting one. Rather than refusing to draw heaven, we draw it at the place Chinese
religious geography already puts it — 泰山 governs the dead, 昆仑 is the pillar of heaven, the 东海 holds the
dragon courts. The map stays readable and the choice is defensible rather than arbitrary.

Coordinates marked `identified` / `projected` / `invented` are first values, to be checked while writing the data.

## 3. Eras: eight arcs over 100 chapters

Eras must tile the range with no gaps (`docs/custom-data.md`). Chapter ranges do that naturally.

| # | id | 名称 | glyph | chapters | What happens |
| --- | --- | --- | --- | --- | --- |
| 1 | `monkey` | 石猴出世 | 猴 | 1–7 | 灵根育孕, 求道于灵台方寸山, 龙宫夺宝, 地府销名, 大闹天宫, 压于五行山 |
| 2 | `mandate` | 取经缘起 | 缘 | 8–12 | 观音访僧, 魏征斩龙, 唐王入冥, 玄奘应诏, 受紫金钵盂 |
| 3 | `disciples` | 收徒聚众 | 徒 | 13–22 | 两界山收悟空, 鹰愁涧收白马, 高老庄收八戒, 流沙河收沙僧 |
| 4 | `demons` | 初历魔难 | 魔 | 23–35 | 五庄观偷果, 三打白骨精, 黑风山, 黄风岭, 平顶山 |
| 5 | `kingdoms` | 王国之难 | 国 | 36–50 | 宝象国, 乌鸡国, 车迟国斗法, 通天河 |
| 6 | `flames` | 火焰山与西域 | 焰 | 51–71 | 红孩儿, 女儿国, 真假美猴王, 火焰山借扇, 朱紫国 |
| 7 | `india` | 天竺诸国 | 竺 | 72–92 | 狮驼岭, 比丘国, 灭法国, 凤仙郡, 玉华州, 金平府 |
| 8 | `sutras` | 灵山取经 | 经 | 93–100 | 天竺国, 凌云渡, 灵山传经, 通天河遇鼋, 五圣成真 |

The timeline sizes bands by the square root of their length, so the 7-chapter 石猴出世 and the 21-chapter
天竺诸国 are both comfortably clickable.

## 4. Events

Target **150–200 events**: the 八十一难 as the spine, plus the set pieces of the first twelve chapters.

```json
{ "id": "ch46-cheqi-contest", "year": 46, "level": 1, "category": "diplomacy",
  "title": "The contest at Cheqi", "title_zh": "车迟国斗法",
  "place": "Kingdom of Cheqi (Karashahr?)", "place_zh": "车迟国（焉耆一带？）",
  "lat": 42.0, "lon": 86.5, "ground": "identified",
  "summary": "… Historically: Xuanzang passed through Agni, around Karashahr, and recorded a dozen Buddhist monasteries …",
  "summary_zh": "师徒与三位国师斗求雨、斗坐禅、隔板猜枚、砍头、剖腹剜心、滚油洗澡…… 史实：玄奘经阿耆尼国（今焉耆一带），记其国有佛寺十余所、僧徒二千余人，习学小乘……" }
```

- `year` is the chapter number.
- `level` drives the detail filter: `1` for the famous episodes (大闹天宫, 三打白骨精, 火焰山), `2` for the rest
  of the 八十一难, `3` for incidental stops.
- `ground` is an extra field. The engine ignores unknown fields, so it costs nothing; the validator checks it
  and the layer builder uses it.
- There is no separate `historical` field: pack events have no story file (`data.details` is not a manifest
  key), so the summary is the only text a card shows, and the 史实 clause lives at its end.
- No `refs` yet. A link to the original chapter would go through the manifest's `refs.url`, but no
  chapter-addressable source has been confirmed (§9, question 3), and a broken link is worse than none.

### Categories are a fixed list — map onto them

`CATS` is hardcoded (`app.js:1663`): `war, politics, reform, rebellion, diplomacy, economy, culture, science,
society`. A pack cannot add its own. The novel's natural categories map on well enough:

| Engine category | 西游记 use |
| --- | --- |
| `war` | 降妖伏魔, any fight |
| `rebellion` | 大闹天宫, 反天庭 |
| `politics` | 天庭封官 (齐天大圣), 唐王遣使, 国王赐爵 |
| `diplomacy` | 过关验牒, 与国王交涉, 斗法赌赛 |
| `reform` | 皈依受戒 (收徒, 立誓, 改过) |
| `culture` | 讲经论道, 诗偈 |
| `science` | 法术, 炼丹, 兵器 (金箍棒, 芭蕉扇) |
| `economy` | 化斋, 布施, 供养 |
| `society` | 人间风俗, 民情, 灾荒 |

Lossy but usable, and the mapping is itself a finding: the filter row ends up answering "show me only the
fights" / "only the kingdom politics", which is a reasonable way to read the book.

## 5. Tours, layers, plugins

**Tours** (`tours.json`), five, with `path: true` so the route draws as it goes (`three-strikes` excepted):

| id | era | Steps |
| --- | --- | --- |
| `monkey-rise` | `monkey` | 花果山 → 灵台方寸山 → 东海龙宫 → 地府 → 天宫 → 五行山 |
| `road-west` | `disciples` | The full pilgrimage in 16 steps, the pack's headline tour |
| `three-strikes` | `demons` | 三打白骨精, 5 steps on one hillside at zoom 7.5–8.5 — tests whether the engine reads at small scale |
| `flaming-mountain` | `flames` | 火焰山 → 芭蕉洞 → 小须弥山 → 摩云洞 → 三调 → 高昌故城, 7 steps |
| `xuanzang-real` | `disciples` | The historical journey, reusing the 8 steps of the atlas's own `xuanzang` tour verbatim, so the two routes can be compared step by step |

`xuanzang-real` is the control group. Running it next to `road-west` is the whole point of the pack.

**Plugins**

- `plugins/realms.js` — the only plugin built. It hides the engine's border layers, polity labels and map line
  (§2.2) and offers them back as the 真实疆域 chip, and hides the Neighbours chip (and its group, once empty).
  The 四大部洲 and 三界 turned out to need no code: they are plain manifest layers.
- *Not built:* `journey.js` (the route already grows with the chapter axis, and `path: true` draws each tour's
  track) and `chapter.js` (回目 couplet titles). Both remain good polish.

## 6. Engine changes — all optional, all small

The pack works without any of these (§1). Each is worth doing afterwards, and each generalizes the engine for
*any* novel, not just this one.

| # | Change | Where | Size |
| --- | --- | --- | --- |
| 1 | **A named axis.** `manifest.axis = { unit, name, name_zh, format, format_zh }`; `fmtYear`, `fmtYearParts` and the search parser consult it. Turns `45年` into `第45回`. | `app.js:141-149`, `app.js:2440-2444` | ~20 lines |
| 2 | **`borders: false`.** A pack that has no territorial history gets `snapshots: [{from, borders: null, world: true}]` — the shape `worldSnaps` already returns when it finds nothing — instead of world maps. Replaces the plugin hack in §2.2. | `addPack`, `app.js:501` | ~2 lines |
| 3 | **Pack-supplied `snapshots`.** Move `...e` after `snapshots`, resolving paths against the manifest. Lets a pack draw its own polities. Not needed here; needed by any pack with borders of its own. | `addPack`, `app.js:503` | ~1 line |
| 4 | **Pack `categories`.** Let the manifest declare its own filter tags with labels, falling back to `CATS`. | `app.js:1663`, `renderEventFilter` | ~10 lines |
| 5 | **Pack `places`.** `packFile()` already documents a `places` key (`app.js:540`) but `init()` never loads it, so a pack shown alone has no city markers. Wire it up. | `init`, `app.js:2803-2806` | ~2 lines |

Change 1 is the one that matters conceptually: it is what turns a history engine into a narrative engine.

## 7. Manifest

```json
{
  "atlas": 1,
  "id": "xiyouji",
  "name": "Journey to the West",
  "name_zh": "西游记",
  "region": {
    "polygon": [[70, 15], [125, 15], [125, 48], [70, 48]],
    "view": { "center": [96, 33], "zoom": 3.4, "year": 13 }
  },
  "range": { "start": 1, "end": 100 },
  "data": { "eras": "eras.json", "events": "events.json", "tours": "tours.json" },
  "layers": [
    { "id": "route", "name": "Road west", "name_zh": "取经路线", "data": "layers/route.geojson",
      "type": "line", "color": "#c47a2c", "width": 3 },
    { "id": "kingdoms", "name": "Kingdoms", "name_zh": "人间国度", "data": "layers/kingdoms.geojson",
      "type": "circle", "color": "#b93a26", "radius": 6 },
    { "id": "continents", "name": "Four continents", "name_zh": "四大部洲", "data": "layers/continents.geojson",
      "type": "fill", "color": "#6b5a7a", "opacity": 0.12, "on": false },
    { "id": "realms", "name": "Three realms", "name_zh": "三界", "data": "layers/realms.geojson",
      "type": "circle", "color": "#7a5195", "radius": 7 }
  ],
  "plugins": ["plugins/realms.js"],
  "attribution": "Journey to the West (1592). Episode geography is partly traditional identification, partly invented.",
  "note": "The axis is the chapter number, not years. Places are real, traditionally identified, projected from religious geography, or invented. Terrain and coastlines are modern.",
  "note_zh": "本图的「年」是回目。地名分四种：史有其地、旧说比附、神话投影、纯属虚构。地形、海岸线和河流均为现代地理。"
}
```

Opened with:

```sh
python3 -m http.server 8000
# http://localhost:8000/?pack=packs/xiyouji/manifest.json&packonly=1
```

A pack on the same site always loads, so no `PACK_ORIGINS` entry is needed (`app.js:14`, `app.js:526`).

## 8. Plan

| Phase | Deliverable | Notes |
| --- | --- | --- |
| **0. Skeleton** | `manifest.json`, `eras.json` (8 eras), 25 events covering 第1–22回, one tour (`monkey-rise`), `realms.js` hiding borders | Half a day. Enough to answer: does a chapter axis feel right? |
| **1. The road** | All 八十一难 as events (~150), `route.geojson`, `kingdoms.geojson`, `road-west` and `xuanzang-real` tours, `journey.js` | The bulk of the work, and it is writing, not coding. |
| **2. Honesty** | `ground` on every place, marker styling by ground, `historical` notes wherever the real journey touches the fictional one | This is what makes the pack worth showing to someone. |
| **3. Generalize** | Engine changes 1 and 2 from §6, on a separate branch | After the data exists, so the change is driven by a real pack. |
| **4. Polish** | 四大部洲, `chapter.js` couplet titles, remaining tours | Optional. |

### Tools

*As built:* phases 0, 1, 2 and 4 are done, phase 3 is not (see §10). The events were written straight into
`events.json` in chunks, so the planned `build_events.py` table converter was not needed. Two tools were:

- `tools/packs/check_pack.py` — checks everything `app.js` silently ignores (era tiling, the nine categories,
  chapter range, coordinate box, footing, tour step targets, layer geometry) and reports coverage per era.
- `tools/xiyouji/build_layers.py` — derives the road from the events and writes all four layers. Rerun it after
  editing events.

## 9. Open questions

1. **Does a 100-unit axis feel right at all three timeline zooms?** The "decades" zoom was built for a few dozen
   years; over 100 chapters it may be useless and should perhaps collapse to two levels. Phase 0 answers this.
2. **Where does 第一回–第七回 go on the map?** 大闹天宫 is the most famous part of the book and has almost no
   earthly geography. If the `projected` anchors read as arbitrary, the alternative is to let those chapters be a
   non-spatial prologue — which the engine cannot express. A real limit, worth finding out early.
3. **Chapter-text link.** Confirm a stable, chapter-addressable source before committing to `refs.url`.
4. **Character set — decided.** Editions of the novel usually print traditional characters, but the atlas's own
   data is simplified throughout, so the pack is simplified too (西游记, not 西遊記). Worth re-checking only if the
   chapter-text source of question 3 turns out to be traditional-only, in which case `refs` labels may look
   inconsistent with the cards.
5. **Is a second novel needed to prove the point?** 《三国演义》 would be the easy case (real years, real
   geography, real borders — it would need nothing but data). 《镜花缘》 or 《山海经》 would be the hard case
   (pure invented geography, which needs the custom-terrain work the engine does not have yet).

## 10. What was built, and what it answered

**Built** (branch `xiyouji`, `packs/xiyouji/`): 8 eras over chapters 1–100; 134 events, at least one in every
chapter; 5 tours; 4 layers; one plugin. Places by footing: 76 invented, 29 identified, 17 projected, 12 real.
33 events (25%) carry a 史实 clause, drawn from the *Biography of the Tripitaka Master* and the *Record of the
Western Regions*. All texts are bilingual. The validator passes with no errors and no warnings.

**Checked in a browser** (headless Chrome driven over CDP, no console errors): the pack loads alone, the timeline
shows the eight bands 猴 缘 徒 魔 国 焰 竺 经, the event list and filters work, the layers toggle, the borders and
their labels stay hidden across chapter changes and come back with the chip, all five tours play, and the
English interface works.

**Answers to §9**

1. *The axis.* It works at all three zooms. The whole-book view reads as a progress bar; the era zoom spreads
   an arc's chapters over the full rail, one tick each. The third zoom adds little for arcs of 21 chapters or
   fewer. What is wrong is the wording, not the mechanics: `45年` / `27 CE`, "each segment is one map", "decades
   view". All of it is engine change 1 in §6.
2. *The first seven chapters.* The `projected` anchors render and the `monkey-rise` tour flies between them
   without trouble; whether 天宫 on the Kunlun and 地府 on Mount Tai *read* as sensible is a judgement for a
   human reader, and the main thing to look at when reviewing.
3. *Chapter links.* Still open; no `refs` until a source is confirmed.
5. *A second novel.* Still worth doing, for the reasons given.

**Findings worth keeping**

- The novel's geography does not run in order. Once places are pinned to their traditional identifications, the
  road jumps: Cheqi at Karashahr (ch. 44), then the Heaven-Reaching River in Qinghai (ch. 47), the Women's
  Country north of the Himalayas (ch. 53), back to Turfan for the Flaming Mountain (ch. 59). The map shows this
  at a glance, which no reading of the text does. It is the clearest evidence that the atlas adds something to a
  novel rather than illustrating it.
- `xuanzang-real` against the novel is the best view in the pack: the historical step and the novel's episode at
  the same place, side by side (e.g. Gaochang and the Flaming Mountain, ch. 59).
- Engine friction, in order of how much it showed: the year wording (§6, change 1); the world borders a pack
  cannot opt out of (change 2, worked around in `realms.js`, including labels and the period card line that
  the original plan missed); the fixed categories (change 4, worked around by the mapping in §4).
- Auto layers (`AUTO_RULES` in `app.js`) can light up the engine's own 路线 / 官道 chips during a tour step even
  though a pack shown alone has no data for them. Cosmetic; a pack-aware `AUTO_RULES` would fix it.
