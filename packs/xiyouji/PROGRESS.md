# Build ledger — Journey to the West pack

State for the `/loop` that fills this pack in. **This file is the single source of truth for what is done.**
Design decisions live in [DESIGN.md](DESIGN.md); do not re-litigate them here.

## Per-iteration procedure

1. Read this file. Take the **first unchecked chunk** in §Chunks. Do only that one.
2. Write the data, following §Contract exactly.
3. Run `python3 tools/xiyouji/check_pack.py`. It must exit 0. Fix what it reports; never commit with errors.
4. `git add -A && git commit` on branch `xiyouji`, message `xiyouji: <chunk name>`.
5. Tick the chunk's box in this file, note the event count, and commit that too (amend into step 4 is fine).
6. If every chunk is ticked, run the validator once more, then **stop the loop**.

Do not skip ahead, do not batch two chunks into one iteration unless the first finishes with plenty of room,
and do not rewrite chunks already ticked.

## Contract

**Axis.** `year` is the chapter number (回), 1–100. Never a calendar year.

**Event shape** — append to `events.json`, written with `json.dumps(data, ensure_ascii=False, indent=1)` so it
matches the repo's own files:

```json
{
 "id": "ch44-cheqi-contest",
 "year": 44,
 "level": 1,
 "category": "diplomacy",
 "title": "The contest at Cheqi",
 "title_zh": "车迟国斗法",
 "place": "Cheqi (Qarashahr?)",
 "place_zh": "车迟国（焉耆一带？）",
 "lat": 42.06,
 "lon": 86.57,
 "ground": "identified",
 "summary": "Three Taoists have the king's favour and set monks to building their temple. Monkey beats them at calling rain, at meditation and at being beheaded.",
 "summary_zh": "三个道士得国王宠信，役使和尚筑观。悟空与之斗求雨、坐禅、砍头，一一取胜。史实：玄奘过焉耆、龟兹，记其国小乘佛法盛行，与小说所写道士当国正相反。"
}
```

- `id`: `ch<NN>-<english-slug>`, `NN` zero-padded to two digits (`ch07-`, `ch100-` as `ch100-`).
- `year`: the chapter the episode starts in. Several events may share a chapter.
- `level`: `1` for the episodes everyone knows (大闹天宫, 三打白骨精, 火焰山借扇, 灵山传经), `2` for the rest of
  the 八十一难, `3` for incidental stops. Roughly 15 / 60 / 25 percent.
- `category`: exactly one of the nine the engine allows, per the mapping in DESIGN.md §4:
  降妖打斗 `war` · 大闹天宫 `rebellion` · 封官受诏 `politics` · 过关验牒·斗法赌赛 `diplomacy` ·
  皈依受戒 `reform` · 讲经论道 `culture` · 法术炼丹兵器 `science` · 化斋布施 `economy` · 风俗民情灾荒 `society`
- `ground`: `real` | `identified` | `projected` | `invented`, per DESIGN.md §2.3. Put the uncertainty in
  `place_zh` too, as a parenthetical with a question mark, so a reader sees it without reading the source.
- `lat`/`lon`: inside lon 65–125, lat 15–48 (the validator enforces it). Reuse these known-good coordinates
  wherever the story touches them:

  | | lon, lat | |
  | --- | --- | --- |
  | 长安 | `108.96, 34.22` | `real` |
  | 玉门关外·莫贺延碛 | `95.8, 40.3` | `real` |
  | 高昌（吐鲁番） | `89.5, 42.9` | `real` |
  | 火焰山 | `89.2, 42.9` | `identified` |
  | 碎叶·素叶城 | `75.4, 42.8` | `real` |
  | 那烂陀寺 | `85.44, 25.13` | `real` |
  | 曲女城 | `79.9, 27.06` | `real` |
  | 于阗 | `79.9, 37.1` | `real` |
  | 花果山（连云港云台山） | `119.4, 34.5` | `identified` |
  | 地府（泰山） | `117.1, 36.25` | `projected` |
  | 天宫（昆仑） | `80.0, 36.0` | `projected` |
  | 龙宫（东海，截到框内） | `122.5, 31.0` | `projected` |
  | 灵台方寸山（西牛贺洲） | `73.0, 34.0` | `projected` |
  | 灵山·凌云渡 | `85.1, 24.7` | `projected` |

  For `invented` lairs, interpolate along the road west between the two nearest anchored places, and nudge off
  the line so markers do not stack — the engine declutters within 18 px.
- `summary` / `summary_zh`: two to four sentences. Where the real journey touches the episode, end `summary_zh`
  with a clause starting `史实：` and `summary` with one starting `Historically:`. That comparison is the point
  of the pack; aim for it on at least a quarter of the events, and never invent a parallel that is not there.
- Simplified characters throughout (西游记, not 西遊記).

**Tour shape** — `tours.json`, same conventions, `era` must be one of the pack's eight era ids, `path: true`,
steps `{year, at: [lon, lat], zoom?, event?, text, text_zh}`. Prefer 8–16 steps. Point `event` at a real event id.

**Layer shape** — GeoJSON FeatureCollection. Feature `properties`: `name`, `name_zh`, `text`, `text_zh`, and
`from`/`to` as **chapter** numbers, range `[from, to)`, so the feature appears and disappears as the axis moves.
`color` overrides the layer colour — use it to show footing: `#2c7a68` real, `#c47a2c` identified,
`#7a5195` projected, `#8a8a5a` invented.

## Chunks

Target: about 180 events total.

- [x] **1. events: monkey (ch 1–7)** — 灵根育孕, 访道, 悟彻菩提, 龙宫夺宝, 地府销名, 官封齐天大圣, 乱蟠桃会, 八卦炉, 压五行山. ~14 events
- [x] **2. events: mandate (ch 8–12)** — 观音奉旨访僧, 魏征斩泾河龙, 唐王入冥, 玄奘应诏, 领通关文牒. ~10 events
- [x] **3. events: disciples (ch 13–22)** — 双叉岭, 两界山收悟空, 紧箍儿, 鹰愁涧白马, 观音院黑熊精, 高老庄收八戒, 黄风岭, 流沙河收沙僧. ~18 events
- [x] **4. events: demons (ch 23–35)** — 四圣试禅心, 五庄观人参果, 三打白骨精, 黑松林宝象国, 平顶山金角银角, 莲花洞, 乌鸡国. ~22 events
- [ ] **5. events: kingdoms (ch 36–50)** — 乌鸡国除妖, 红孩儿号山, 黑水河, 车迟国斗法, 通天河灵感大王, 金兜洞. ~24 events
- [ ] **6. events: flames (ch 51–71)** — 如来助降, 女儿国落胎泉, 真假美猴王, 火焰山借芭蕉扇, 祭赛国碧波潭, 荆棘岭, 小雷音, 朱紫国, 盘丝洞. ~32 events
- [ ] **7. events: india (ch 72–92)** — 狮驼岭, 比丘国, 陷空山无底洞, 灭法国, 隐雾山, 凤仙郡求雨, 玉华州, 金平府犀牛. ~30 events
- [ ] **8. events: sutras (ch 93–100)** — 天竺国玉兔, 铜台府, 凌云渡脱胎, 灵山传经, 无字真经, 通天河老鼋沉经, 五圣成真. ~14 events
- [ ] **9. layers: route.geojson + kingdoms.geojson** — the road west as ~10 segments with `from`/`to` chapters so it grows; the ten kingdoms as points with cards.
- [ ] **10. layers: realms.geojson + continents.geojson** — 天宫·地府·龙宫·灵山 as four `projected` points; 四大部洲 as four deliberately vague polygons, clipped to the pack's box.
- [ ] **11. tours: `monkey-rise` + `road-west`** — the rise and fall of Monkey (花果山 → 方寸山 → 龙宫 → 地府 → 天宫 → 五行山); the whole pilgrimage in 16 steps. `road-west` is the headline tour.
- [ ] **12. tours: `three-strikes` + `flaming-mountain` + `xuanzang-real`** — `xuanzang-real` copies the eight steps of the atlas's own `xuanzang` tour from `data/tours.json` verbatim (text included), with `year` remapped to the chapter each step corresponds to, so the real journey and the novel can be played side by side.
- [ ] **13. finish** — run the validator; write `packs/xiyouji/README.md` (what it is, the open URL, what the four footings mean, one screenshot-less paragraph on known limits); reconcile DESIGN.md with what was actually built, including the two corrections noted below; final commit.

### Corrections to fold into DESIGN.md in chunk 13

- Pack events have no story file (`data.details` is not a manifest key), so the `historical` field in DESIGN.md §4
  does not exist: the史实 note lives inside `summary_zh` instead. Update §4's example.
- `ground` is not rendered on event markers — the engine builds those itself and a plugin cannot restyle them.
  It is rendered as feature `color` on the pack's own layers, and carried in `place_zh` as a parenthetical.
  Update §2.3 and §5's description of `realms.js`.
- `realms.js` ended up smaller than §5 describes: it hides the engine's border layers and offers them back as a
  真实疆域 chip, and hides the now-meaningless Neighbours chip. No marker styling, no card rewriting.

## Done

(iterations append one line each: chunk, event count, commit)
- chunk 1, events for the monkey era (ch 1-7): 16 events from the stone monkey to Five Elements Mountain; heaven, the underworld and the dragon court placed at their projected earthly sites. (events total 16)
- chunk 2, events for the mandate era (ch 8-12): 14 events from the Buddha's offer at Vulture Peak to Taizong sending Xuanzang west; the closing event sets the novel's imperial send-off against the real illegal departure. (events total 30)
- chunk 3, events for the disciples era (ch 13-22): 16 events from leaving Chang'an to Sandy at the River of Flowing Sands; Shi Pantuo, the Heart Sutra and the Mokhayan desert set against Wukong, the hermit and the Flowing Sands. (events total 46)
- chunk 4, events for the demons era (ch 23-35): 16 events from the four saints' test to the calabash of Lotus Flower Cave. Wuji, listed under this chunk in the plan, starts at chapter 36 and belongs to the kingdoms era. (events total 62)
