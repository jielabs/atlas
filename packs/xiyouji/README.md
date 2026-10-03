# Journey to the West (西游记)

A data pack that puts the novel *Journey to the West* (1592) on the atlas: all hundred chapters as a timeline,
the pilgrimage and the Monkey King's adventures as events and tours, and the novel's own geography as map layers.
It is also a test of whether a history engine can carry fiction; [DESIGN.md](DESIGN.md) explains the choices and
§10 there records what the test found.

## Open it

```sh
python3 -m http.server 8000        # from the repository root
```

| | |
| --- | --- |
| The pack | <http://localhost:8000/?pack=packs/xiyouji/manifest.json&packonly=1> |
| The headline tour | <http://localhost:8000/?pack=packs/xiyouji/manifest.json&packonly=1#tour=road-west&s=1> |
| The real journey against the novel | <http://localhost:8000/?pack=packs/xiyouji/manifest.json&packonly=1#tour=xuanzang-real&s=1> |
| In English | add `&lang=en` before the `#` |

**The timeline is chapters, not years.** Where the interface says `45年` or `45 CE`, read chapter 45.

## What is in it

| | |
| --- | --- |
| Eras | 8 arcs over chapters 1–100: 石猴出世 · 取经缘起 · 收徒聚众 · 初历魔难 · 王国之难 · 火焰山与西域 · 天竺诸国 · 灵山取经 |
| Events | 134, at least one in every chapter. A quarter end with a 史实 / *Historically* note where Xuanzang's real journey of 629–645 touches the episode. |
| Tours | `road-west` (16 stops), `monkey-rise`, `three-strikes`, `flaming-mountain`, and `xuanzang-real`, the atlas's own historical tour with each step moved to the chapter where the novel reaches the same place |
| Layers | 取经路线 (the road, growing chapter by chapter), 人间国度 (the kingdoms), 三界 (heaven, the underworld, the dragon court, Spirit Mountain), 四大部洲 (off by default), 真实疆域 (the real world map, off by default) |

## How sure each place is

Every place has a footing. On the road and the kingdoms it is the colour; in the event cards it is the
parenthetical with a question mark in the place name.

| Footing | Colour | Meaning | Example |
| --- | --- | --- | --- |
| real | green | The place exists and the story goes there | 长安, 舍卫城祇园 |
| identified | orange | A fictional name with a traditional real-world match | 火焰山 → 吐鲁番, 车迟国 → 焉耆 |
| projected | purple | A mythic place drawn where Chinese religion puts it on earth | 地府 → 泰山, 天宫 → 昆仑 |
| invented | olive | No defensible match; placed along the road between its neighbours | most demon caves |

## Changing it

- Edit `events.json`, `tours.json` or `eras.json` by hand. Keep the conventions in [PROGRESS.md](PROGRESS.md)
  (§Contract): `year` is the chapter, nine allowed categories, a footing on every place, JSON written with
  `indent=1` and `ensure_ascii=False`.
- `python3 tools/packs/check_pack.py packs/xiyouji` checks the pack. It catches what the atlas would silently ignore.
- `python3 tools/xiyouji/build_layers.py` rebuilds the four layers. The road is derived from the events, so
  rerun it after moving or adding one.

## Known limits

- Interface wording assumes years: `年` / `CE` after numbers, "each segment is one map", "decades view". Fixing
  it needs a small engine change (DESIGN.md §6, change 1).
- The road jumps about, because the traditional identifications do not follow the novel's order (the
  Heaven-Reaching River is in Qinghai, the Women's Country north of the Himalayas). That is the honest result,
  not a bug.
- Identifications are traditional and loose, and invented places are placed by interpolation.
- Summaries and historical notes were drafted with an AI model from general knowledge of the novel, the
  *Biography of the Tripitaka Master* and the *Record of the Western Regions*, and have not been checked line by
  line against the texts.
- No links to the chapter text yet: no stable chapter-addressable source has been confirmed.
- During some tour steps the engine's auto-layers chip may name 路线 / 官道, layers a pack shown alone does not have.
- Terrain, coastlines and rivers are modern, as everywhere in the atlas.
