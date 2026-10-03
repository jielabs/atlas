# Build ledger — Romance of the Three Kingdoms pack

Same procedure as [the Journey to the West ledger](../xiyouji/PROGRESS.md): take the first unchecked chunk, write
it to the contract, run `python3 tools/packs/check_pack.py packs/sanguo` (must exit 0), commit, tick.

## How this pack differs from Journey to the West

Journey to the West has a fictional route across real ground, so its uncertainty is about **places** (`ground`).
The Three Kingdoms has real places and real dates, so its uncertainty is about **events** (`truth`). The axis is
real years, 184–280, and the chapter is a field. Borders are real too, drawn from commandery seats
(`tools/sanguo/states.json`, built by `tools/sanguo/build_borders.py`).

## Contract

```json
{
 "id": "ch005-hua-xiong",
 "year": 190,
 "chapter": 5,
 "level": 1,
 "category": "war",
 "truth": "fiction",
 "title": "Guan Yu kills Hua Xiong before the wine cools",
 "title_zh": "温酒斩华雄",
 "place": "Sishui Pass",
 "place_zh": "汜水关（今河南荥阳汜水镇）",
 "lat": 34.86,
 "lon": 113.2,
 "summary": "… Historically: Hua Xiong was killed by Sun Jian's army at Yangren …",
 "summary_zh": "……史实：《三国志·孙坚传》载华雄为孙坚所斩，地点在阳人，与关羽无关。"
}
```

- `id`: `ch<NNN>-<english-slug>`, chapter zero-padded to three digits.
- `year`: the real year the episode belongs to (the novel follows the historical chronology closely). `chapter`:
  the chapter it is told in, 1–120 (毛宗岗本). Every chapter gets at least one event.
- `truth`:
  - `history` — recorded essentially as told, in the *Records of the Three Kingdoms* (三国志) or the *Book of the
    Later Han* (后汉书).
  - `embellished` — a real event the novel changes: credit moved to another hero, numbers inflated, details added.
  - `fiction` — the novel's invention, or a later legend it adopts.
- `embellished` and `fiction` events **must** end with `史实：` / `Historically:` saying what the sources do say
  (the validator enforces it). `history` events may carry one for useful context.
- `level`: `1` for the episodes everyone knows, `2` for the main plot, `3` for detail. `category`: the nine the
  engine allows (rebellion for the Yellow Turbans and mutinies, diplomacy for alliances and envoys, science for
  inventions, medicine and stratagems of craft, economy for farming colonies and supply).
- Coordinates: the Han site where possible, with the modern place in `place_zh` (`赤壁（今湖北赤壁西北）`).
- JSON written with `indent=1`, `ensure_ascii=False`; simplified characters.

## Chunks

- [ ] **1. events ch 1–9** (184–192): 桃园结义 to the fall of Dong Zhuo
- [ ] **2. events ch 10–21** (193–199): the warlords, Lü Bu, Cao Cao and the emperor
- [ ] **3. events ch 22–38** (199–208): Guandu, Guan Yu's five passes, the three visits
- [ ] **4. events ch 39–57** (208–210): Changban, the Red Cliffs, Zhou Yu's three angers
- [ ] **5. events ch 58–77** (211–220): Tong Pass, Yizhou, Hanzhong, Guan Yu's fall
- [ ] **6. events ch 78–85** (220–223): three emperors, Yiling, Baidi
- [ ] **7. events ch 86–104** (224–234): the southern campaign and the northern expeditions
- [ ] **8. events ch 105–120** (234–280): the Sima, Jiang Wei, the fall of Shu, Jin
- [ ] **9. layers**: capitals, Guan Yu's five passes, the northern expeditions, truth halos under the event markers
- [ ] **10. tours**: Guan Yu, the Red Cliffs, Zhuge Liang, Liu Bei's life, the road to unity
- [ ] **11. finish**: README, browser check, docs

## Done

