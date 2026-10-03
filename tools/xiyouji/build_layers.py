"""Build the pack's four layers: the road west, the kingdoms, the three realms and the four continents.

Usage: python3 tools/xiyouji/build_layers.py        (writes packs/xiyouji/layers/*.geojson)

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

# The realms beyond the human world, each drawn at the earthly site Chinese religion already gives it.
P = FOOTING["projected"]
REALMS = [
 ("Heavenly Palace", "天宫", 80.0, 36.0,
  "The Jade Emperor's court, where Wukong kept the horses, guarded the peaches and wrecked the banquet (ch. 4-7). Drawn on the Kunlun, the pillar of heaven and home of the Queen Mother of the West.",
  "玉帝的天庭，悟空在此做弼马温、看蟠桃园、大闹天宫（第4–7回）。投影在昆仑山：昆仑是天柱，也是西王母的居所。"),
 ("The underworld", "幽冥地府", 117.1, 36.25,
  "The ten courts of the dead, where Wukong struck out his name and Taizong pleaded his case (ch. 3, 10-11, 58, 97). Drawn on Mount Tai, which in Chinese belief governed the souls of the dead.",
  "十殿阎罗所在，悟空在此勾销生死簿，唐太宗在此对质还魂（第3、10–11、58、97回）。投影在泰山：旧俗以泰山主治鬼魂。"),
 ("Dragon Palace of the Eastern Sea", "东海龙宫", 122.5, 31.0,
  "Where Wukong took the gold-banded staff (ch. 3) and went to sulk after his first quarrel with Tripitaka (ch. 14). Drawn in the East China Sea.",
  "悟空在此取得金箍棒（第3回），第一次与唐僧闹翻后也到这里散心（第14回）。投影在东海。"),
 ("Spirit Mountain", "灵山", 85.45, 25.0,
  "The Buddha's Thunderclap Monastery, the end of the road (ch. 8, 58, 98, 100). Drawn on Vulture Peak outside Rajgir, where the Buddha is said to have preached, a few miles from Nalanda where Xuanzang studied.",
  "如来的雷音寺，取经路的终点（第8、58、98、100回）。投影在王舍城外的灵鹫山，相传佛陀在此说法，距玄奘求学的那烂陀寺不远。"),
]
rf = [{"type": "Feature", "properties": {"name": n, "name_zh": nz, "text": t, "text_zh": tz, "color": P},
       "geometry": {"type": "Point", "coordinates": [lon, lat]}} for n, nz, lon, lat, t, tz in REALMS]
dump(f"{PACK}/layers/realms.geojson", {"type": "FeatureCollection", "features": rf})

# The four continents of Buddhist cosmology, as the novel uses them. Deliberately soft ellipses, clamped to the
# pack's box: the book says which continent a place is in, never where one ends.
W, E, S, N = 65.0, 125.0, 15.0, 48.0
def blob(cx, cy, rx, ry, n=36):
    ring = [[round(min(E, max(W, cx + rx * math.cos(2 * math.pi * i / n))), 2),
             round(min(N, max(S, cy + ry * math.sin(2 * math.pi * i / n))), 2)] for i in range(n)]
    return {"type": "Polygon", "coordinates": [ring + [ring[0]]]}
CONTINENTS = [
 ("Purvavideha, the eastern continent", "东胜神洲", (121.5, 32.0, 3.5, 7.0), "#4f8f86",
  "Home of Flower-Fruit Mountain. The Buddha: its people revere heaven and earth, and are clear-hearted and even-tempered (ch. 8).",
  "花果山所在。如来说：东胜神洲者，敬天礼地，心爽气平（第8回）。"),
 ("Jambudvipa, the southern continent", "南赡部洲", (109.0, 32.0, 8.5, 9.0), "#b5523b",
  "The Tang empire. The Buddha: its people are greedy and lustful, delight in trouble, and kill and quarrel much, which is why it needs the scriptures (ch. 8).",
  "大唐所在。如来说：南赡部洲者，贪淫乐祸，多杀多争，所以要传经劝善（第8回）。"),
 ("Aparagodaniya, the western continent", "西牛贺洲", (82.0, 31.0, 17.0, 13.0), "#c47a2c",
  "Everything beyond Two Frontiers Mountain, all the way to Spirit Mountain. The Buddha: its people neither covet nor kill, and nourish the spirit (ch. 8). The demons on the road suggest otherwise.",
  "两界山以西直到灵山都属此洲。如来说：我西牛贺洲者，不贪不杀，养气潜灵（第8回）。一路妖魔却不大像。"),
 ("Uttarakuru, the northern continent", "北俱芦洲", (105.0, 46.0, 18.0, 2.5), "#6a8aa0",
  "Never visited in the story. The Buddha: its people kill, but only to eat, and are simple and do little harm (ch. 8).",
  "书中师徒从未到过。如来说：北俱芦洲者，虽好杀生，只因糊口，性拙情疏，无多作践（第8回）。"),
]
cf = [{"type": "Feature", "properties": {"name": n, "name_zh": nz, "text": t, "text_zh": tz, "color": c},
       "geometry": blob(*g)} for n, nz, g, c, t, tz in CONTINENTS]
dump(f"{PACK}/layers/continents.geojson", {"type": "FeatureCollection", "features": cf})
print(f"route: {len(stations)} stations, {len(legs)} legs; kingdoms: {len(kf)}; realms: {len(rf)}; continents: {len(cf)}")
