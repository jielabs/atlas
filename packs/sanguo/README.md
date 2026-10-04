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
| Events | 272, at least two in every chapter (the two halves of its couplet title) and more where the novel is busiest. The novel leads: an episode is here because the novel tells it, and placed where the novel places it. 146 history, 71 embellished, 55 invented; every embellished or invented one ends with a 史实 / *Historically* note saying what the sources record |
| Borders | 17 maps: the atlas's Eastern Han map for 184–190, then sixteen warlord and Three Kingdoms maps from 191 to 280, grown from the seats of 109 Eastern Han commanderies |
| Army movements | 60 marches, coloured by side and pointed with arrowheads, each shown in its own years: the coalition against Dong Zhuo, Guandu and the march beyond the Wall, Changban and the Red Cliffs, the taking of Shu and Hanzhong, Fancheng and the fall of Jingzhou, Yiling, the southern campaign, the five northern expeditions and Wei's answers, Liaodong, Jiang Wei, the conquest of Shu and of Wu |
| Tours | 23, 252 steps; in 87 of them an army marches across the map as the camera flies. **Battles:** `anti-dong`, `guandu`, `changban`, `red-cliffs`, `tongguan`, `into-shu`, `hanzhong`, `fall-of-jingzhou`, `yiling`, `southern-campaign`, `northern-expeditions`, `fall-of-shu`, `fall-of-wu`. **People:** `cao-cao`, `liu-bei`, `guan-yu`, `zhuge-liang`, `zhao-yun`, `lu-bu`, `sun-family`, `sima-yi`, `jiang-wei`. **Overview:** `road-to-unity`. Every step is tagged 【正史】, 【演义加工】 or 【虚构】 |
| Layers | 行军路线 (the army movements), 正史·演义·虚构 (the coloured disc under each event marker), 都城 (capitals with their years), 过五关路线 (Guan Yu's fictional ride) |

## How true each episode is

| Mark | Disc | Meaning | Examples |
| --- | --- | --- | --- |
| `history` | green | Recorded essentially as told, in the *Records of the Three Kingdoms* or the *Book of the Later Han* | 官渡之战, 白门楼, 单骑救主 (the core), 邓艾偷渡阴平 |
| `embellished` | amber | A real event the novel changes: credit moved, numbers inflated, details added | 单刀赴会 (it was Lu Su's challenge), 水淹七军 (the rain did it), 三让徐州 (once, not three times) |
| `fiction` | purple | The novel's invention, or a later legend | 桃园结义, 温酒斩华雄, 过五关斩六将, 草船借箭, 空城计 |

The discs follow the event markers exactly, including the detail and topic filters, because a small plugin
(`plugins/truth.js`) recomputes them with the engine's own rules.

## Army movements

`plugins/campaigns.js` draws `layers/campaigns.geojson`: each march as a line in its side's colour (曹魏 blue, 蜀汉
green, 孙吴 red, 袁绍 purple, 吕布 orange, 董卓 plum, 晋 slate) with arrowheads in the direction of march, shown only in
the years it happened. When a tour step names marches, they are drawn out from start to finish while the camera
flies, and stay highlighted until the next step. The lines join the places the novel names, so they sketch a route
rather than survey it.

## Changing it

- Events, tours and eras are plain JSON. The contract is in [PROGRESS.md](PROGRESS.md): real `year`, `chapter`
  1–120, a `truth` mark, a 史实 note on anything not plain history, `indent=1` and `ensure_ascii=False`.
- `python3 tools/packs/check_pack.py packs/sanguo` checks the pack, including that every embellished or invented
  event explains itself and that every chapter has an event.
- Borders: edit `tools/sanguo/states.json` (one line per change of hands) and run
  `python3 tools/sanguo/build_borders.py` (needs shapely). Then add the map to the era in `eras.json`.
- `python3 tools/sanguo/build_layers.py` rebuilds the capitals, the five passes and the army movements. A march is
  one line in its `CAMPAIGNS` table: a side, its years, its chapters, and the places it passes through by name (from
  the `P` table of Han sites). A tour step names marches in `"route": [...]` and `plugins/campaigns.js` animates them.

## Publishing

The pack is published as a stand-alone site in two environments, built by `tools/sanguo/build_site.py` (150 MB with
all tiles for the region). The page names the pack in `<html data-pack>`, so addresses stay clean, and every build
writes `version.json` (commit, branch, uncommitted changes, build time), so each environment says what it runs.

| | Development | Production |
| --- | --- | --- |
| Address | <https://atlas.yangjie.org/> | <https://sanguo.yangjie.org/> |
| Host | nginx on the VPS `dev`, behind Cloudflare | Cloudflare Workers static assets, no server |
| Marked | " · dev" after the name, `robots.txt` keeps search engines out | — |
| Publish | `tools/sanguo/deploy_dev.sh` (any state of the tree) | `tools/sanguo/deploy_prod.sh` (only what dev runs) |

The workflow: commit, push, publish to dev and look at it there, then promote. `deploy_prod.sh` refuses to run with
uncommitted changes, with a commit that is not on GitHub, or when dev runs a different commit; `--force` skips the
last check for an urgent fix.

Development, from a workstation (`deploy_dev.sh` copies to `jie@dev:/var/www/atlas`), or on the server itself, which
needs only Python 3 and rsync:

```sh
git clone --depth 1 -b sanguo git@github.com:jielabs/atlas.git && cd atlas
tools/sanguo/deploy_dev.sh /var/www/atlas      # later: git pull --ff-only && tools/sanguo/deploy_dev.sh /var/www/atlas
```

The dev site is proxied by Cloudflare (SSL mode Full, or Full (strict)) to nginx, whose site is in
`tools/sanguo/nginx/`; its Let's Encrypt certificate is issued and renewed through the webroot `/var/www/acme`.

Production needs `npx wrangler login` once on the machine that publishes. `tools/sanguo/wrangler.jsonc` binds
sanguo.yangjie.org as a Workers custom domain, so Cloudflare keeps its DNS record and certificate; the `_headers`
file from `build_site.py --pages` caches the tile archives for 30 days and types the `.geojson` files.

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
