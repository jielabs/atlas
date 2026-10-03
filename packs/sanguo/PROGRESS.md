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

- [x] **1. events ch 1–9** (184–192): 桃园结义 to the fall of Dong Zhuo
- [x] **2. events ch 10–21** (193–199): the warlords, Lü Bu, Cao Cao and the emperor
- [x] **3. events ch 22–38** (199–208): Guandu, Guan Yu's five passes, the three visits
- [x] **4. events ch 39–57** (208–210): Changban, the Red Cliffs, Zhou Yu's three angers
- [x] **5. events ch 58–77** (211–220): Tong Pass, Yizhou, Hanzhong, Guan Yu's fall
- [x] **6. events ch 78–85** (220–223): three emperors, Yiling, Baidi
- [x] **7. events ch 86–104** (224–234): the southern campaign and the northern expeditions
- [x] **8. events ch 105–120** (234–280): the Sima, Jiang Wei, the fall of Shu, Jin
- [x] **9. layers**: capitals, Guan Yu's five passes, the northern expeditions, truth halos under the event markers
- [x] **10. tours**: Guan Yu, the Red Cliffs, Zhuge Liang, Liu Bei's life, the road to unity
- [ ] **11. finish**: README, browser check, docs

## Done

- chunk 1, events ch 1-9 (184-192): 19 events from the peach garden to Li Jue and Guo Si: 8 history, 7 embellished, 4 fiction. The oath, Hua Xiong, the three heroes against Lü Bu and Diaochan are the novel's; Zhang Fei's whipping was Liu Bei's own. (events total 19)
- chunk 2, events ch 10-21 (193-199): 20 events from Cao Cao's revenge in Xuzhou to Che Zhou. More history than chunk 1: the halberd at the camp gate, Taishi Ci against Sun Ce and Lü Bu's end are all in the Records; Xutian, the plum wine and the swallowed eye are the embellishments. (events total 39)
- chunk 3, events ch 22-38 (199-208): 25 events from Wang Zhong and Liu Dai to Huang Zu. Guan Yu's year shows the pattern: Yan Liang and the sealed gifts are history, Wen Chou and Cai Yang were other men's kills, and the five passes are pure invention. (events total 64)
- chunk 4, events ch 39-57 (208-210): 27 events from Bowang to Pang Tong at Leiyang. The Red Cliffs chapters are the novel at its most inventive: the arrows, the beating, the chained ships, the east wind and Huarong are all fiction around a battle that is history. (events total 91)
- chunk 5, events ch 58-77 (211-220): 32 events from Tong Pass to Jade Spring Hill. Two reversals stand out: Ma Teng was killed because Ma Chao rebelled, not the other way round, and the single-sword meeting was Lu Su's challenge to Guan Yu. (events total 123)
- chunk 6, events ch 78-85 (220-223): 14 events from Hua Tuo to the five armies. This stretch is mostly history: Cao Cao's death, the two enthronements, Zhang Fei's murder, Yiling and the charge at Baidi are all recorded; Hua Tuo is twelve years late and the seven-step poem is a later legend. (events total 137)
- chunk 7, events ch 86-104 (224-234): 29 events from Qin Mi's riddles to Wuzhang Plains. The empty fort is the clearest case of the novel taking a real trick from one hero (Zhao Yun, 219) and giving it to another; the seven captures, the second memorial and the seven lamps are flagged as doubtful or invented. (events total 166)
- chunk 8, events ch 105-120 (234-280): 27 events from Wei Yan's death to the surrender of Wu. The last stretch is almost all history: the Sima coup, Cao Mao's death, Deng Ai at Yinping, Liu Shan's 'happy here' and Wang Jun's fleet are told as the sources tell them. Every chapter now has an event. (events total 193)
- chunk 9, layers: truth halos, capitals, five passes, expeditions: tools/sanguo/build_layers.py writes four layers: a disc under every event coloured by truth and shown for the same years as the marker (derived from events.json), eleven capitals with their years, Guan Yu's fictional ride through five passes, and Zhuge Liang's five northern campaigns kept on the map until Shu falls. (events total 193)
- chunk 10, tours: Guan Yu, the Red Cliffs, Zhuge Liang, Liu Bei, the road to unity: Five tours, 68 steps, each step tagged history / embellished / fiction. Guan Yu and the Red Cliffs are the two where invention is densest; the road to unity is there to watch the borders change from one Han to a dozen warlords to three states to one Jin. (events total 193)
