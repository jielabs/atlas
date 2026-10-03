"""Build the Three Kingdoms pack's map layers.

Usage: python3 tools/sanguo/build_layers.py        (writes packs/sanguo/layers/*.geojson)

- truth.geojson: a coloured disc under every event marker (green history, amber embellished, purple fiction), shown
  for the same years the engine shows the marker, so the map says at a glance how much of a stretch is invented.
  Derived from events.json; rerun after editing events.
- capitals.geojson: the capitals of the court and the three states, each for the years it served.
- five-passes.geojson: Guan Yu's fictional ride through five passes (chapter 27), which runs hundreds of li out of
  its way.
- expeditions.geojson: Zhuge Liang's five northern campaigns, 228-234, each staying on the map until Shu falls.
"""
import json

PACK = "packs/sanguo"
TRUTH = {"history": ("#2c7a68", "Recorded history", "正史有载"),
         "embellished": ("#c9a227", "Real, but embellished by the novel", "史有其事，演义加工"),
         "fiction": ("#8a4f9e", "The novel's invention", "小说虚构")}
# app.js keeps an event on the map from its year for max(2, era length / 60) more years; every era here is
# under 120 years long, so that is two.
ACTIVE = 3


def dump(name, features):
    with open(f"{PACK}/layers/{name}.geojson", "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=1) + "\n")
    print(f"{name}: {len(features)} features")


def point(lon, lat, **props):
    return {"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": [lon, lat]}}


def line(coords, **props):
    return {"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": coords}}


events = json.load(open(f"{PACK}/events.json", encoding="utf-8"))
dump("truth", [point(e["lon"], e["lat"], color=TRUTH[e["truth"]][0], **{"from": e["year"], "to": e.get("endYear", e["year"]) + ACTIVE},
                     name=f"{TRUTH[e['truth']][1]}: {e['title']}", name_zh=f"{TRUTH[e['truth']][2]}：{e['title_zh']}",
                     text=f"Chapter {e['chapter']}.", text_zh=f"第{e['chapter']}回。")
               for e in events])

HAN, WEI, SHU, WU, YUAN = "#2c7a68", "#3f6e8c", "#4f7f5a", "#b5523b", "#9a8a4a"
CAPITALS = [
 (112.62, 34.72, 184, 191, HAN, "Luoyang, capital of the Han", "洛阳（东汉都城）", "Until Dong Zhuo burned it and moved the court west in 190–191.", "190–191年董卓焚城西迁之前的东汉都城。"),
 (108.94, 34.27, 191, 196, HAN, "Chang'an, the court under Dong Zhuo and his generals", "长安（献帝西迁）", "The emperor's prison under Dong Zhuo, then Li Jue and Guo Si, until his escape in 195–196.", "董卓及李傕、郭汜挟持献帝之地，直到195–196年献帝东归。"),
 (116.78, 32.57, 197, 200, YUAN, "Shouchun, Yuan Shu's capital", "寿春（袁术称帝）", "Where Yuan Shu proclaimed his short-lived dynasty in 197.", "197年袁术在此称帝，国号仲，两年而亡。"),
 (113.85, 34.03, 196, 221, HAN, "Xu, the Han court under Cao Cao", "许都（汉献帝）", "Cao Cao kept the emperor here from 196 until the end of the Han in 220.", "196年曹操迎献帝都许，至220年汉亡。"),
 (114.35, 36.3, 204, 221, WEI, "Ye, Cao Cao's seat", "邺城（曹操、魏王）", "Cao Cao's base after 204, capital of his Wei kingdom from 213.", "204年曹操取邺后的根据地，213年起为魏公、魏王国都。"),
 (112.23, 30.06, 209, 214, SHU, "Gong'an, Liu Bei's Jingzhou seat", "公安（刘备驻荆州）", "Liu Bei's headquarters after the Red Cliffs.", "赤壁之战后刘备在荆州的治所。"),
 (104.07, 30.67, 214, 264, SHU, "Chengdu, capital of Shu Han", "成都（蜀汉都城）", "Liu Bei's capital from 214, the Shu Han capital from 221 until the surrender of 263.", "214年刘备取益州，221年称帝都此，至263年降魏。"),
 (118.8, 32.05, 212, 221, WU, "Jianye, Sun Quan's seat", "建业（孙权）", "Sun Quan moved here, renaming Moling, in 212.", "212年孙权移治秣陵，改名建业。"),
 (114.88, 30.4, 221, 229, WU, "Wuchang, Sun Quan's capital", "武昌（孙权）", "Sun Quan's capital while he faced Shu and Wei from the middle Yangzi.", "孙权为对付蜀、魏，移都武昌。"),
 (118.8, 32.05, 229, 281, WU, "Jianye, capital of Wu", "建业（吴国都城）", "Capital of Wu from Sun Quan's enthronement in 229 until the surrender of 280.", "229年孙权称帝后都建业，至280年降晋。"),
 (112.62, 34.72, 220, 281, WEI, "Luoyang, capital of Wei and Jin", "洛阳（魏、晋都城）", "Rebuilt as the capital of Wei from 220, and of Jin from 265.", "220年起重建为魏都，265年起为晋都。"),
]
dump("capitals", [point(lon, lat, color=c, name=n, name_zh=nz, text=t, text_zh=tz, **{"from": a, "to": b})
                  for lon, lat, a, b, c, n, nz, t, tz in CAPITALS])

FICTION = TRUTH["fiction"][0]
PASSES = [  # (lon, lat, place, place_zh, general, general_zh)
 (113.85, 34.03, "Xu", "许都", None, None),
 (112.95, 34.45, "Dongling Pass", "东岭关", "Kong Xiu", "孔秀"),
 (112.62, 34.72, "Luoyang", "洛阳", "Han Fu and Meng Tan", "韩福、孟坦"),
 (113.2, 34.86, "Sishui Pass", "汜水关", "Bian Xi", "卞喜"),
 (113.38, 34.79, "Xingyang", "荥阳", "Wang Zhi", "王植"),
 (114.65, 35.55, "the Yellow River ford", "黄河渡口", "Qin Qi", "秦琪"),
 (114.5, 33.1, "Gucheng", "古城", "Cai Yang", "蔡阳"),
]
legs = []
for (x0, y0, p0, p0z, _, _z), (x1, y1, p1, p1z, g, gz) in zip(PASSES, PASSES[1:]):
    legs.append(line([[x0, y0], [x1, y1]], color=FICTION, **{"from": 200, "to": 202},
                     name=f"Guan Yu's ride: {p0} → {p1}", name_zh=f"千里走单骑：{p0z} → {p1z}",
                     text=f"Chapters 27–28. Kills {g} at {p1}. None of it happened, and none of these men is in the histories."
                          " Dongling Pass is placed approximately; the novel gives no location.",
                     text_zh=f"第27–28回。在{p1z}斩{gz}。史书并无此事，这些守将也都不见于史书。东岭关位置为示意，小说未说明所在。"))
dump("five-passes", legs)

HZ = [107.03, 33.07]
EXPEDITIONS = [
 (228, "First expedition: through Qishan to Jieting", "第一次北伐：出祁山，失街亭", [HZ, [106.4, 33.5], [105.4, 34.1], [105.83, 34.95]],
  "Three commanderies go over; Ma Su loses Jieting and the army falls back.", "三郡叛魏响应，马谡失街亭，全军撤回。"),
 (228, "First expedition: Zhao Yun's decoy at Ji Valley", "第一次北伐：赵云出箕谷为疑兵", [HZ, [107.05, 33.6]],
  "The decoy column that drew Cao Zhen's main army.", "牵制曹真主力的疑兵。"),
 (228, "Second expedition: the siege of Chencang", "第二次北伐：围陈仓", [HZ, [106.7, 33.6], [106.98, 34.27], [107.15, 34.37]],
  "Hao Zhao holds Chencang for twenty days; Wang Shuang dies in the pursuit. (Winter 228–229.)", "郝昭坚守陈仓二十余日，蜀军粮尽而退，斩追将王双。（228年冬至229年初）"),
 (229, "Third expedition: Wudu and Yinping", "第三次北伐：取武都、阴平", [HZ, [105.7, 33.75], [104.68, 32.95]],
  "The one lasting gain of the northern campaigns.", "历次北伐中唯一长期守住的战果。"),
 (231, "Fourth expedition: Qishan, Shanggui and Mumen", "第四次北伐：出祁山，割上邽之麦，木门道射杀张郃", [HZ, [106.4, 33.5], [105.4, 34.1], [105.7, 34.58], [105.55, 34.35]],
  "Wooden oxen carry the grain; Zhang He is killed at Mumen in the retreat.", "以木牛运粮；退兵时于木门道射杀张郃。"),
 (234, "Fifth expedition: up the Xie Valley to Wuzhang Plains", "第五次北伐：出斜谷，屯五丈原", [HZ, [107.3, 33.5], [107.55, 33.95], [107.65, 34.28]],
  "A hundred days facing Sima Yi across the Wei; Zhuge Liang dies in camp.", "与司马懿隔渭水对峙百余日，诸葛亮病逝军中。"),
]
dump("expeditions", [line(c, color=SHU, name=n, name_zh=nz, text=t, text_zh=tz, **{"from": y, "to": 264})
                     for y, n, nz, c, t, tz in EXPEDITIONS])
