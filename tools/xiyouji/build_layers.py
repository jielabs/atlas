"""Build the pack's road-west and kingdoms layers.

Usage: python3 tools/xiyouji/build_layers.py        (writes packs/xiyouji/layers/route.geojson and kingdoms.geojson)

The road is derived from events.json, so it follows whatever the events say: the pilgrimage events in chapter
order, from the send-off in Chang'an (chapter 12) to the return (chapter 100), skipping the episodes that happen
elsewhere (Flower-Fruit Mountain, the underworld, Spirit Mountain mid-journey). Nearby events merge into one
station. Each leg carries `from` = the chapter the pilgrims arrive, and no `to`, so the road grows as the
timeline moves. A leg is coloured by the footing of the place it arrives at, so the road shows where the novel
can be pinned down and where it is guesswork. Rerun after editing events.
"""
import json, math

PACK = "packs/xiyouji"
FOOTING = {"real": "#2c7a68", "identified": "#c47a2c", "projected": "#7a5195", "invented": "#8a8a5a"}
FOOTING_ZH = {"real": "史有其地", "identified": "旧说比附", "projected": "神话投影", "invented": "纯属虚构"}
# Episodes that leave the road: Wukong's trips home, to the Buddha, to the underworld.
OFF_ROAD = {"ch28-monkeys-reassemble", "ch31-bajie-fetches-wukong", "ch57-false-monkey",
            "ch58-six-eared-macaque", "ch97-kou-hong-revived"}
MERGE_DEG = 0.6   # events closer than this to the current station belong to it

def dump(path, fc):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(fc, ensure_ascii=False, indent=1) + "\n")

events = json.load(open(f"{PACK}/events.json", encoding="utf-8"))
road = [e for e in events if 12 <= e["year"] <= 100 and e["id"] not in OFF_ROAD
        and not (e["year"] == 12 and e["id"] != "ch12-sent-west")]
road.sort(key=lambda e: (e["year"], events.index(e)))

# Stations: runs of events near each other. Keep the first event's place name and footing.
stations = []
for e in road:
    s = stations[-1] if stations else None
    if s and math.dist((s["lon"], s["lat"]), (e["lon"], e["lat"])) < MERGE_DEG:
        s["last"] = e["year"]
        continue
    stations.append({"lon": e["lon"], "lat": e["lat"], "first": e["year"], "last": e["year"],
                     "place": e["place"], "place_zh": e["place_zh"], "ground": e["ground"]})

legs = []
for a, b in zip(stations, stations[1:]):
    span = f"{b['first']}" if b["first"] == b["last"] else f"{b['first']}–{b['last']}"
    legs.append({"type": "Feature", "properties": {
        "name": f"{a['place']} → {b['place']}", "name_zh": f"{a['place_zh']} → {b['place_zh']}",
        "text": f"Chapter {span}. Arrival point: {b['ground']}.",
        "text_zh": f"第{span}回。到达地点：{FOOTING_ZH[b['ground']]}。",
        "from": b["first"], "color": FOOTING[b["ground"]]},
        "geometry": {"type": "LineString", "coordinates": [[round(a["lon"], 2), round(a["lat"], 2)],
                                                           [round(b["lon"], 2), round(b["lat"], 2)]]}})
dump(f"{PACK}/layers/route.geojson", {"type": "FeatureCollection", "features": legs})

# The kingdoms of men the pilgrims pass through, each appearing when they arrive and staying on the map.
KINGDOMS = [
 ("Great Tang", "大唐", 108.96, 34.22, "real", 1,
  "Emperor Taizong's empire, capital Chang'an. The pilgrimage starts and ends here (ch. 9-13, 100).",
  "唐太宗的大唐，都城长安。取经从这里出发，也回到这里（第9–13回、第100回）。"),
 ("Baoxiang", "宝象国", 91.3, 42.6, "invented", 29,
  "Its princess was carried off by the Yellow Robe Monster, the Wolf Star, for thirteen years (ch. 28-31).",
  "公主百花羞被黄袍怪（奎木狼）摄去十三年（第28–31回）。"),
 ("Wuji", "乌鸡国", 89.6, 41.15, "invented", 37,
  "Its king lay three years drowned in a well while Manjusri's lion ruled in his shape (ch. 36-39).",
  "国王被推入井中三年，文殊的青毛狮子变作他的模样坐了王位（第36–39回）。"),
 ("Cheqi", "车迟国", 86.57, 42.06, "identified", 44,
  "Ruled by three Taoist masters who enslaved the monks, until the contest of magic (ch. 44-46). Placed at Agni (Karashahr), which Xuanzang visited.",
  "三位道士国师当国，和尚沦为苦力，直到斗法（第44–46回）。比附为玄奘经过的阿耆尼国（焉耆）。"),
 ("Western Liang, the Women's Country", "西梁女国", 80.5, 31.5, "identified", 53,
  "A kingdom of women whose queen offered Tripitaka her throne (ch. 53-54). Placed at the Eastern Women's Kingdom of the Record of the Western Regions.",
  "女儿国，女王愿以一国之富招唐僧为王（第53–54回）。比附为《大唐西域记》所载东女国。"),
 ("Jisai", "祭赛国", 87.6, 42.5, "invented", 62,
  "Its pagoda's relic was stolen by the nine-headed bird of Green Wave Lake (ch. 62-63).",
  "金光寺宝塔佛宝被碧波潭九头虫盗走（第62–63回）。"),
 ("Zhuzi", "朱紫国", 83.5, 41.4, "invented", 68,
  "Its king pined three years for a queen taken by Guanyin's golden-haired hou (ch. 68-71).",
  "国王因金圣宫娘娘被观音坐骑金毛犼摄去，相思成病三年（第68–71回）。"),
 ("Lion-Camel Kingdom", "狮驼国", 78.3, 41.6, "invented", 74,
  "A kingdom eaten whole by the Great Peng five hundred years before the pilgrims came (ch. 74-77).",
  "五百年前被大鹏金翅雕吃尽满城君臣百姓，成了妖城（第74–77回）。"),
 ("Bhiksu", "比丘国", 76.2, 40.6, "invented", 78,
  "A deer spirit, the king's father-in-law, demanded 1,111 children's hearts (ch. 78-79).",
  "国丈白鹿精要用一千一百一十一个小儿心肝做药引（第78–79回）。"),
 ("The Law-Destroying Kingdom", "灭法国", 72.0, 34.6, "invented", 84,
  "Its king had killed 9,996 monks before Wukong shaved the whole court bald (ch. 84).",
  "国王已杀九千九百九十六个和尚，被悟空一夜剃光满朝头发，改名钦法国（第84回）。"),
 ("India", "天竺国", 79.9, 27.06, "identified", 93,
  "Its princess was replaced by the Jade Rabbit (ch. 93-95). Placed at Kanyakubja, Harsha's capital.",
  "公主被月宫玉兔顶替（第93–95回）。比附为戒日王都城曲女城。"),
]
kf = [{"type": "Feature", "properties": {"name": n, "name_zh": nz, "text": t, "text_zh": tz, "from": fr,
       "color": FOOTING[g]}, "geometry": {"type": "Point", "coordinates": [lon, lat]}}
      for n, nz, lon, lat, g, fr, t, tz in KINGDOMS]
dump(f"{PACK}/layers/kingdoms.geojson", {"type": "FeatureCollection", "features": kf})
print(f"route: {len(stations)} stations, {len(legs)} legs; kingdoms: {len(kf)}")
