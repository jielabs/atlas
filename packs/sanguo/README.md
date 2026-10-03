# Romance of the Three Kingdoms (三国演义)

A data pack that puts the novel *Romance of the Three Kingdoms* on the atlas: 96 years from the Yellow Turbans to
the unification under Jin, every one of the 120 chapters as events, the warlords' territories year by year, and a
mark on every episode saying whether it is history, history embellished, or the novel's invention.

It is the companion to [Journey to the West](../xiyouji/README.md), and the opposite case. Journey to the West
puts a fictional route on real ground, so its doubt is about **places**. The Three Kingdoms has real places and
real dates, so its doubt is about **what happened**: the saying is that it is seven parts history, three parts
invention, and the pack shows which parts are which.

## Open it

```sh
python3 -m http.server 8000        # from the repository root
```

| | |
| --- | --- |
| The pack | <http://localhost:8000/?pack=packs/sanguo/manifest.json&packonly=1> |
| Guan Yu, man and legend | <http://localhost:8000/?pack=packs/sanguo/manifest.json&packonly=1#tour=guan-yu&s=1> |
| The Red Cliffs | <http://localhost:8000/?pack=packs/sanguo/manifest.json&packonly=1#tour=red-cliffs&s=1> |
| In English | add `&lang=en` before the `#` |

The chip at the top left switches between this pack, Journey to the West and the atlas itself.

## What is in it

| | |
| --- | --- |
| Eras | 10, real years 184–280: 黄巾之乱 · 董卓乱政 · 群雄割据 · 官渡与北定 · 赤壁之战 · 三分天下 · 三国鼎立 · 诸葛北伐 · 司马专权 · 三分归晋 |
| Events | 193, at least one in every chapter. 113 history, 53 embellished, 27 invented; every embellished or invented one ends with a 史实 / *Historically* note saying what the sources record |
| Borders | 17 maps: the atlas's Eastern Han map for 184–190, then sixteen warlord and Three Kingdoms maps from 191 to 280, grown from the seats of 109 Eastern Han commanderies |
| Tours | `guan-yu`, `red-cliffs`, `zhuge-liang`, `liu-bei`, `road-to-unity`; every step is tagged 【正史】, 【演义加工】 or 【虚构】 |
| Layers | 正史·演义·虚构 (the coloured disc under each event marker), 都城 (capitals with their years), 过五关路线 (Guan Yu's fictional ride), 诸葛北伐 (the five northern campaigns) |

## How true each episode is

| Mark | Disc | Meaning | Examples |
| --- | --- | --- | --- |
| `history` | green | Recorded essentially as told, in the *Records of the Three Kingdoms* or the *Book of the Later Han* | 官渡之战, 白门楼, 单骑救主 (the core), 邓艾偷渡阴平 |
| `embellished` | amber | A real event the novel changes: credit moved, numbers inflated, details added | 单刀赴会 (it was Lu Su's challenge), 水淹七军 (the rain did it), 三让徐州 (once, not three times) |
| `fiction` | purple | The novel's invention, or a later legend | 桃园结义, 温酒斩华雄, 过五关斩六将, 草船借箭, 空城计 |

The discs follow the event markers exactly, including the detail and topic filters, because a small plugin
(`plugins/truth.js`) recomputes them with the engine's own rules.

## Changing it

- Events, tours and eras are plain JSON. The contract is in [PROGRESS.md](PROGRESS.md): real `year`, `chapter`
  1–120, a `truth` mark, a 史实 note on anything not plain history, `indent=1` and `ensure_ascii=False`.
- `python3 tools/packs/check_pack.py packs/sanguo` checks the pack, including that every embellished or invented
  event explains itself and that every chapter has an event.
- Borders: edit `tools/sanguo/states.json` (one line per change of hands) and run
  `python3 tools/sanguo/build_borders.py` (needs shapely). Then add the map to the era in `eras.json`.
- `python3 tools/sanguo/build_layers.py` rebuilds the capitals, the five passes and the expeditions.

## Known limits

- Warlord borders are grown from commandery seats, so their edges are indicative only; between the snapshot years
  the map shows the last one.
- The truth marks are judgements about a novel that mixes sources freely; where historians disagree (the seven
  captures of Meng Huo, the second memorial) the note says so.
- Summaries and historical notes were drafted with an AI model from general knowledge of the novel, the *Records*
  with Pei Songzhi's notes, the *Book of the Later Han* and the *Book of Jin*, and have not been checked line by
  line against the texts.
- In the decades zoom the engine narrows the event window further than the discs do, so a few extra discs can
  show there.
- During some tour steps the engine's auto-layers chip may name layers (Armies, Passes) a pack shown alone does not
  have.
- The interface still says `年` / `CE`; here that is correct, since the years are real.
