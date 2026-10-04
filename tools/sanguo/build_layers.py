"""Build the Three Kingdoms pack's static map layers. (The truth discs under the event markers are computed live
by packs/sanguo/plugins/truth.js, since they must follow the engine's period and filters.)

Usage: python3 tools/sanguo/build_layers.py        (writes packs/sanguo/layers/*.geojson)

- capitals.geojson: the capitals of the court and the three states, each for the years it served.
- five-passes.geojson: Guan Yu's fictional ride through five passes (chapter 27), which runs hundreds of li out of
  its way.
- campaigns.geojson: army movements, above all of the great battles, drawn by plugins/campaigns.js with
  arrowheads and animated on tour steps that name them (Zhuge Liang's northern campaigns among them).
"""
import json

PACK = "packs/sanguo"
FICTION = "#8a4f9e"   # the same purple plugins/truth.js uses for invented episodes


def dump(name, features):
    with open(f"{PACK}/layers/{name}.geojson", "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=1) + "\n")
    print(f"{name}: {len(features)} features")


def point(lon, lat, **props):
    return {"type": "Feature", "properties": props, "geometry": {"type": "Point", "coordinates": [lon, lat]}}


def line(coords, **props):
    return {"type": "Feature", "properties": props, "geometry": {"type": "LineString", "coordinates": coords}}


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

# Army movements: one feature per march, in the direction of march, drawn by plugins/campaigns.js with arrowheads and
# animated on tour steps that name them. Coordinates are Han sites; the line joins the places the novel names, so it
# is a sketch of the route, not a survey of it.
P = {
    "酸枣": [114.2, 35.25], "汜水关": [113.2, 34.86], "虎牢关": [113.25, 34.82], "荥阳": [113.38, 34.79], "鲁阳": [112.9, 33.73],
    "阳人": [112.65, 34.25], "洛阳": [112.62, 34.72], "弘农": [110.87, 34.52], "长安": [108.94, 34.27], "华阴": [110.08, 34.56],
    "曹阳": [110.95, 34.6], "安邑": [111.2, 35.14], "鄄城": [115.5, 35.57], "彭城": [117.18, 34.26], "郯": [118.35, 34.6],
    "河内": [113.35, 35.1], "陈留": [114.55, 34.66], "濮阳": [115.03, 35.75], "历阳": [118.35, 31.7], "牛渚": [118.48, 31.65],
    "曲阿": [119.57, 32.0], "吴": [120.6, 31.3], "会稽": [120.58, 30.0], "许": [113.85, 34.03], "宛": [112.53, 33.0],
    "下邳": [117.96, 34.33], "邺": [114.35, 36.3], "黎阳": [114.55, 35.68], "白马": [114.65, 35.55], "延津": [114.2, 35.15],
    "官渡": [114.05, 34.78], "乌巢": [114.42, 35.07], "南皮": [116.7, 38.05], "易": [115.5, 39.05], "无终": [117.4, 40.03],
    "卢龙塞": [118.86, 40.4], "白狼山": [119.7, 41.1], "柳城": [120.4, 41.6], "樊城": [112.15, 32.07], "襄阳": [112.13, 32.01],
    "新野": [112.36, 32.52], "当阳": [111.8, 30.85], "长坂": [111.78, 30.82], "汉津": [113.0, 30.6], "夏口": [114.28, 30.55],
    "江陵": [112.2, 30.35], "石首": [112.4, 29.72], "乌林": [113.45, 29.95], "赤壁": [113.62, 29.88], "樊口": [114.85, 30.37],
    "柴桑": [115.98, 29.7], "华容": [112.85, 29.75], "公安": [112.23, 30.06], "武陵": [111.7, 29.0], "长沙": [112.97, 28.2],
    "零陵": [111.6, 26.4], "桂阳": [113.0, 25.8], "潼关": [110.25, 34.6], "蒲阪": [110.32, 34.85], "渭南": [109.5, 34.5],
    "冀": [105.25, 34.75], "陈仓": [107.15, 34.37], "夷陵": [111.3, 30.7], "白帝": [109.57, 31.04], "江州": [106.55, 29.56],
    "涪": [104.75, 31.47], "葭萌": [105.82, 32.43], "雒": [104.4, 30.98], "成都": [104.07, 30.67], "遂宁": [105.6, 30.5],
    "合肥": [117.25, 31.85], "濡须": [117.86, 31.43], "建业": [118.8, 32.05], "皖": [116.05, 30.52], "散关": [106.98, 34.27],
    "河池": [105.95, 33.75], "阳平关": [106.55, 33.15], "南郑": [107.03, 33.07], "定军山": [106.68, 33.1], "斜谷口": [107.6, 34.2],
    "褒谷口": [106.95, 33.2], "荆门": [112.2, 31.0], "寻阳": [115.9, 29.75], "陆口": [113.8, 29.68], "麦城": [111.92, 30.68],
    "临沮": [111.68, 31.07], "秭归": [110.98, 30.83], "猇亭": [111.42, 30.55], "僰道": [104.6, 28.75], "越巂": [102.25, 27.9],
    "泸水": [102.85, 26.65], "滇池": [102.62, 24.88], "味县": [103.8, 25.5], "祁山": [105.4, 34.1], "街亭": [105.83, 34.95],
    "箕谷": [107.05, 33.6], "上邽": [105.7, 34.58], "木门": [105.55, 34.35], "五丈原": [107.65, 34.28], "武都": [105.7, 33.75],
    "阴平": [104.68, 32.95], "新城": [110.25, 32.25], "陇关": [106.6, 34.85], "孤竹": [118.85, 39.98], "辽隧": [122.4, 41.0],
    "襄平": [123.17, 41.27], "沓中": [103.6, 34.05], "狄道": [103.85, 35.4], "段谷": [105.5, 34.45], "骆谷": [107.9, 33.8],
    "长城": [108.2, 34.05], "剑阁": [105.52, 32.28], "江油": [104.75, 31.78], "绵竹": [104.2, 31.35], "西陵": [111.2, 30.75],
    "武昌": [114.88, 30.4],
}
SIDES = {"cao": ("#3f6e8c", "Cao Cao / Wei", "曹操·魏"), "liu": ("#4f7f5a", "Liu Bei / Shu", "刘备·蜀"),
         "sun": ("#b5523b", "the Sun / Wu", "孙氏·吴"), "yuan": ("#7a5195", "Yuan Shao", "袁绍"),
         "lubu": ("#c47a2c", "Lü Bu", "吕布"), "dong": ("#8a4f6e", "Dong Zhuo", "董卓"), "jin": ("#46637d", "Jin", "晋"),
         "han": ("#2c7a68", "the Han court", "汉廷"), "lords": ("#9a8a4a", "the eastern lords", "关东诸侯"),
         "ma": ("#9a6a3a", "Ma Chao", "马超")}
# (id, side, first year, last year, chapters, name, name_zh, text, text_zh, legs): a leg is a list of place names.
CAMPAIGNS = [
 ("lords-advance", "lords", 190, 190, "5", "The eastern lords advance on Hulao Pass", "诸侯进兵虎牢关",
  "The coalition moves from Suanzao to the passes guarding Luoyang (in the novel, Hua Xiong and the three heroes against Lü Bu).",
  "关东联军自酸枣进逼汜水关、虎牢关（小说中温酒斩华雄、三英战吕布即在此）。", [["酸枣", "汜水关", "虎牢关"]]),
 ("sun-jian-luoyang", "sun", 190, 191, "5–6", "Sun Jian fights his way to Luoyang", "孙坚进军洛阳",
  "Sun Jian beats Dong Zhuo's army at Yangren and is first into the burned capital.", "孙坚阳人破董卓军，率先进入被焚的洛阳。",
  [["鲁阳", "阳人", "洛阳"]]),
 ("dong-zhuo-west", "dong", 190, 190, "6", "Dong Zhuo drags the court west", "董卓挟天子西迁",
  "Dong Zhuo burns Luoyang and forces the emperor and a million people west to Chang'an.", "董卓焚洛阳，驱赶天子与百万百姓西迁长安。",
  [["洛阳", "弘农", "华阴", "长安"]]),
 ("cao-bianshui", "cao", 190, 190, "6", "Cao Cao pursues Dong Zhuo alone", "曹操追击董卓",
  "Cao Cao alone pursues, and is routed by Xu Rong on the Bian River.", "诸侯中唯曹操追击，在汴水被徐荣击败。", [["酸枣", "荥阳"]]),
 ("cao-xuzhou", "cao", 193, 194, "10–11", "Cao Cao's revenge on Xuzhou", "曹操兴兵报父仇",
  "Cao Cao marches from Yan province into Xuzhou to avenge his father.", "曹操自兖州攻入徐州，为父报仇。", [["鄄城", "彭城", "郯"]]),
 ("lubu-yanzhou", "lubu", 194, 195, "11–12", "Lü Bu seizes Yan province", "吕布袭取兖州",
  "With Chen Gong and Zhang Miao, Lü Bu takes Yan province behind Cao Cao's back.", "吕布得陈宫、张邈之助，趁曹操东征袭取兖州。",
  [["河内", "陈留", "濮阳"]]),
 ("emperor-east", "han", 195, 196, "13", "The emperor's flight east", "献帝东归",
  "The court escapes Chang'an, is chased and robbed, crosses the Yellow River at night and comes home to the ruins of Luoyang.",
  "献帝逃出长安，一路被追兵抢掠，夜渡黄河，回到满目疮痍的洛阳。", [["长安", "华阴", "弘农", "曹阳", "安邑", "洛阳"]]),
 ("emperor-to-xu", "cao", 196, 196, "14", "Cao Cao takes the emperor to Xu", "曹操迎帝都许",
  "Cao Cao brings the court from Luoyang to his base at Xu.", "曹操将朝廷从洛阳迁到自己的根据地许县。", [["洛阳", "许"]]),
 ("sun-ce-east", "sun", 194, 196, "15", "Sun Ce crosses the Yangzi and takes Jiangdong", "孙策平定江东",
  "From Liyang Sun Ce crosses at Niuzhu and takes Qu'e, Wu and Kuaiji in two years.", "孙策自历阳牛渚渡江，两年间取曲阿、吴郡、会稽。",
  [["历阳", "牛渚", "曲阿", "吴", "会稽"]]),
 ("wancheng", "cao", 197, 197, "16", "Cao Cao marches on Wan", "曹操征张绣",
  "Zhang Xiu surrenders and then rises in the night; Dian Wei dies at the gate.", "张绣先降后反，夜袭曹营，典韦战死。", [["许", "宛"]]),
 ("xiapi-campaign", "cao", 198, 198, "18–19", "Cao Cao marches on Lü Bu", "曹操东征吕布",
  "Cao Cao takes Pengcheng, floods Xiapi and ends Lü Bu at the White Gate Tower.", "曹操攻取彭城，水淹下邳，白门楼斩吕布。",
  [["许", "彭城", "下邳"]]),
 ("yuan-south", "yuan", 200, 200, "25–30", "Yuan Shao comes south", "袁绍大军南下",
  "Yan Liang besieges Baima; the main army crosses the Yellow River at Yanjin and closes on Guandu.",
  "颜良围白马，袁绍主力自延津渡河，进逼官渡。", [["邺", "黎阳", "白马"], ["黎阳", "延津", "官渡"]]),
 ("cao-guandu", "cao", 200, 200, "25–30", "Cao Cao holds Guandu", "曹操拒守官渡",
  "Cao Cao comes up from Xu to Guandu, and rides out to relieve Baima, where Guan Yu kills Yan Liang.",
  "曹操自许都进屯官渡，并出兵解白马之围，关羽斩颜良。", [["许", "官渡"], ["官渡", "延津", "白马"]]),
 ("wuchao-raid", "cao", 200, 200, "30", "The night raid on Wuchao", "夜袭乌巢",
  "Cao Cao leads five thousand men under Yuan banners to burn Yuan Shao's grain.", "曹操亲率五千人打着袁军旗号夜袭乌巢，焚烧袁绍粮草。",
  [["官渡", "乌巢"]]),
 ("cao-north", "cao", 202, 205, "31–33", "Cao Cao takes the north", "曹操平定河北",
  "After Guandu Cao Cao crosses the river, takes Ye and pursues Yuan Tan to Nanpi.", "官渡之后曹操渡河北上，攻克邺城，追斩袁谭于南皮。",
  [["官渡", "黎阳", "邺", "南皮"]]),
 ("wuhuan", "cao", 207, 207, "33", "Beyond the Wall to White Wolf Mountain", "北征乌桓",
  "Through the Lulong pass and five hundred li of empty country to White Wolf Mountain and Liucheng.",
  "出卢龙塞，穿越五百里荒野，直抵白狼山、柳城。", [["邺", "易", "无终", "卢龙塞", "白狼山", "柳城"]]),
 ("cao-south", "cao", 208, 208, "40–42", "Cao Cao comes south", "曹操南征荆州",
  "Liu Cong surrenders; Cao Cao's cavalry ride three hundred li in a day and night to catch Liu Bei at Changban.",
  "刘琮投降，曹操轻骑一日一夜行三百余里，在长坂追上刘备。", [["宛", "新野", "樊城", "襄阳", "长坂", "江陵"]]),
 ("liu-bei-flight", "liu", 208, 208, "41–42", "Liu Bei flees south with the people", "刘备携民南撤",
  "From Fancheng past Xiangyang to Changban, then east to the Han ford and Xiakou.", "自樊城经襄阳南撤至长坂，再东走汉津，到达夏口。",
  [["樊城", "襄阳", "当阳", "长坂", "汉津", "夏口"]]),
 ("cao-downriver", "cao", 208, 208, "45–48", "Cao Cao's fleet comes down the Yangzi", "曹军顺江东下",
  "From Jiangling the northern army sails down to Wulin, facing the Red Cliffs.", "曹军自江陵顺江东下，屯兵乌林，与赤壁隔江相望。",
  [["江陵", "石首", "乌林"]]),
 ("zhou-yu-west", "sun", 208, 208, "44–49", "Zhou Yu sails west to the Red Cliffs", "周瑜西进赤壁",
  "Zhou Yu and Cheng Pu bring thirty thousand men up the river from Chaisang.", "周瑜、程普率三万水军自柴桑溯江西上。",
  [["柴桑", "樊口", "赤壁"]]),
 ("liu-bei-chibi", "liu", 208, 208, "44–49", "Liu Bei joins Zhou Yu", "刘备会师樊口",
  "From Xiakou Liu Bei moves to Fankou and joins the Wu fleet.", "刘备自夏口移屯樊口，与东吴水军会合。", [["夏口", "樊口"]]),
 ("huarong-retreat", "cao", 208, 208, "50", "Cao Cao's retreat by Huarong", "曹操败走华容道",
  "Through the marshes to Jiangling, then north to Xu, leaving Cao Ren to hold Jiangling.",
  "曹操经华容道穿越沼泽退至江陵，留曹仁守江陵，自己北还许都。", [["乌林", "华容", "江陵"], ["江陵", "襄阳", "宛", "许"]]),
 ("zhou-yu-jiangling", "sun", 209, 209, "51", "Zhou Yu besieges Jiangling", "周瑜攻打南郡",
  "A year's siege of Cao Ren in Jiangling.", "周瑜围攻据守江陵的曹仁一年。", [["赤壁", "石首", "江陵"]]),
 ("jingnan", "liu", 209, 209, "52–53", "Liu Bei takes the four southern commanderies", "刘备取荆南四郡",
  "Zhang Fei to Wuling, Guan Yu to Changsha, Zhao Yun to Guiyang, Liu Bei and Zhuge Liang to Lingling.",
  "张飞取武陵，关羽取长沙，赵云取桂阳，刘备、诸葛亮取零陵。", [["公安", "武陵"], ["公安", "长沙", "桂阳"], ["长沙", "零陵"]]),
 ("cao-tongguan", "cao", 211, 211, "58–59", "Cao Cao to Tong Pass and across the Yellow River", "曹操西征潼关",
  "Cao Cao faces Ma Chao at Tong Pass, slips across the river at Puban and wins south of the Wei.",
  "曹操在潼关与马超对峙，从蒲阪津北渡黄河，再南渡渭水，大破关中联军。", [["邺", "洛阳", "潼关"], ["潼关", "蒲阪", "渭南"]]),
 ("ma-chao-east", "ma", 211, 211, "58", "Ma Chao marches on Tong Pass", "马超兴兵潼关",
  "Ma Chao and Han Sui bring the armies of the northwest to Tong Pass.", "马超、韩遂率关西诸军进据潼关。", [["冀", "陈仓", "长安", "潼关"]]),
 ("into-shu", "liu", 211, 212, "60–62", "Liu Bei goes up the Yangzi into Shu", "刘备入川",
  "Invited by Liu Zhang, Liu Bei sails up through the gorges to Jiangzhou, meets Liu Zhang at Fu and goes on to Jiameng.",
  "应刘璋之邀，刘备溯江穿越三峡到江州，在涪城与刘璋相会，再北上葭萌。", [["公安", "夷陵", "白帝", "江州", "涪", "葭萌"]]),
 ("take-chengdu", "liu", 212, 214, "62–65", "Liu Bei turns on Liu Zhang", "刘备进取成都",
  "From Jiameng back south through Fu and Luo to Chengdu, while Zhuge Liang, Zhang Fei and Zhao Yun come up the river from Jiangzhou.",
  "刘备自葭萌回师，经涪城、雒城南下成都；诸葛亮、张飞、赵云自江州溯江分路来会。", [["葭萌", "涪", "雒", "成都"], ["江州", "遂宁", "雒"]]),
 ("cao-ruxu", "cao", 213, 213, "61", "Cao Cao at Ruxu", "曹操进军濡须",
  "Cao Cao comes south from Hefei to the Ruxu dyke; after a month he goes home.", "曹操自合肥南下濡须口，相持月余而还。", [["合肥", "濡须"]]),
 ("sun-ruxu", "sun", 213, 213, "61", "Sun Quan holds Ruxu", "孙权拒守濡须",
  "Sun Quan comes up from Jianye to hold the fort at Ruxu.", "孙权自建业进屯濡须坞。", [["建业", "濡须"]]),
 ("sun-hefei", "sun", 215, 215, "67", "Sun Quan marches on Hefei", "孙权进攻合肥",
  "A hundred thousand men against Hefei, until Zhang Liao's eight hundred charge at Xiaoyao Ford.",
  "孙权率十万大军进攻合肥，被张辽八百人在逍遥津冲破。", [["柴桑", "皖", "合肥"]]),
 ("cao-hanzhong", "cao", 215, 215, "67", "Cao Cao takes Hanzhong", "曹操平定汉中",
  "Through the Dasan Pass and over the mountains to Yangping, where Zhang Lu's defences give way.",
  "曹操出散关翻越秦岭，攻破阳平关，张鲁投降。", [["长安", "陈仓", "散关", "河池", "阳平关", "南郑"]]),
 ("liu-hanzhong", "liu", 218, 219, "70–72", "Liu Bei marches on Hanzhong", "刘备进取汉中",
  "From Chengdu by the Jinniu road to Yangping Pass and Mount Dingjun, where Huang Zhong kills Xiahou Yuan.",
  "刘备自成都经金牛道北上阳平关、定军山，黄忠斩夏侯渊。", [["成都", "涪", "葭萌", "阳平关", "定军山"]]),
 ("cao-hanzhong-219", "cao", 219, 219, "71–72", "Cao Cao comes to save Hanzhong, and leaves", "曹操争夺汉中",
  "Down the Xie valley road to Yangping; after months of stalemate, 'chicken rib', and back the same way.",
  "曹操经褒斜道南下阳平，相持数月，以“鸡肋”为令，原路撤回。", [["长安", "斜谷口", "褒谷口", "阳平关"]]),
 ("guan-yu-north", "liu", 219, 219, "73–74", "Guan Yu marches north", "关羽北伐襄樊",
  "From Jiangling up the Han to Xiangyang and Fancheng, where the autumn floods drown seven armies.",
  "关羽自江陵沿汉水北上，围攻襄阳、樊城，秋雨汉水泛滥，水淹七军。", [["江陵", "荆门", "襄阳", "樊城"]]),
 ("xu-huang-relief", "cao", 219, 219, "76", "Xu Huang relieves Fancheng", "徐晃救援樊城",
  "From Wan, Xu Huang breaks through Guan Yu's siege lines.", "徐晃自宛城南下，冲破关羽的围城营垒。", [["宛", "樊城"]]),
 ("lu-meng", "sun", 219, 219, "75", "Lü Meng crosses in white", "吕蒙白衣渡江",
  "From Xunyang, soldiers hidden in merchant boats, past the beacons to Gong'an and Jiangling.",
  "吕蒙自寻阳出发，精兵藏于商船，白衣摇橹，袭取公安、江陵。", [["寻阳", "陆口", "公安", "江陵"]]),
 ("guan-yu-retreat", "liu", 219, 219, "76–77", "Guan Yu's last retreat", "关羽败走麦城",
  "Jiangling lost behind him, Guan Yu falls back to Maicheng and breaks out towards Shu, to the ambush at Linju.",
  "后方江陵已失，关羽退守麦城，突围西走，在临沮遭伏被擒。", [["樊城", "襄阳", "当阳", "麦城", "临沮"]]),
 ("yiling-advance", "liu", 221, 222, "81–84", "Liu Bei marches down the gorges against Wu", "刘备东征孙吴",
  "From Chengdu down the Yangzi through Baidi and Zigui to Yiling and Xiaoting.", "刘备自成都顺江东下，经白帝、秭归，进抵夷陵、猇亭。",
  [["成都", "江州", "白帝", "秭归", "夷陵", "猇亭"]]),
 ("lu-xun-fire", "sun", 222, 222, "84", "Lu Xun's counter-attack", "陆逊火攻反击",
  "Lu Xun fires the Shu camps one after another along the river.", "陆逊沿江火攻，连破蜀军四十余营。", [["夷陵", "猇亭"]]),
 ("yiling-retreat", "liu", 222, 222, "84–85", "Liu Bei flees to Baidi", "刘备败退白帝",
  "The beaten army falls back up the gorges to Baidi, where Liu Bei will die.", "蜀军大败，刘备溯江退回白帝城，次年病逝于此。",
  [["猇亭", "秭归", "白帝"]]),
 ("southern-campaign", "liu", 225, 225, "87–90", "Zhuge Liang marches south", "诸葛亮南征",
  "From Chengdu by Bodao and Yuexi, across the Lu in the fifth month, to Dian and Wei.", "诸葛亮自成都经僰道、越巂，五月渡泸，深入南中。",
  [["成都", "僰道", "越巂", "泸水", "滇池", "味县"]]),
 ("expedition-1", "liu", 228, 228, "91–95", "First expedition: through Qishan", "第一次北伐：出祁山",
  "Out through Qishan; three commanderies go over; Ma Su loses Jieting.", "出祁山，三郡响应，马谡失街亭。",
  [["南郑", "祁山", "冀"], ["冀", "街亭"]]),
 ("zhao-yun-decoy", "liu", 228, 228, "92", "Zhao Yun's decoy at Ji Valley", "赵云出箕谷",
  "The decoy column up the Ji Valley road.", "赵云率疑兵出箕谷。", [["南郑", "箕谷"]]),
 ("sima-yi-meng-da", "cao", 228, 228, "94", "Sima Yi's march on Meng Da", "司马懿奔袭孟达",
  "Twelve hundred li in eight days from Wan to Xincheng.", "司马懿自宛城八日行一千二百里，奔袭新城孟达。", [["宛", "新城"]]),
 ("zhang-he-jieting", "cao", 228, 228, "95", "Zhang He to Jieting", "张郃驰援街亭",
  "From Chang'an over the Long road to Jieting, where he cuts off Ma Su's water.", "张郃自长安越陇关西进街亭，断马谡汲水之道。",
  [["长安", "陇关", "街亭"]]),
 ("expedition-2", "liu", 228, 228, "97–98", "Second expedition: Chencang", "第二次北伐：攻陈仓",
  "Through the Dasan Pass against Hao Zhao's Chencang.", "出散关，围攻郝昭据守的陈仓。", [["南郑", "散关", "陈仓"]]),
 ("expedition-3", "liu", 229, 229, "99", "Third expedition: Wudu and Yinping", "第三次北伐：取武都阴平",
  "Chen Shi takes Wudu and Yinping.", "陈式攻取武都、阴平。", [["南郑", "武都", "阴平"]]),
 ("expedition-4", "liu", 231, 231, "101", "Fourth expedition: Qishan and Shanggui", "第四次北伐：出祁山割麦",
  "Out through Qishan to reap the wheat at Shanggui; Zhang He dies at Mumen in the retreat.", "出祁山，割上邽之麦，退兵时于木门道射杀张郃。",
  [["南郑", "祁山", "上邽", "木门"]]),
 ("expedition-5", "liu", 234, 234, "102–104", "Fifth expedition: up the Xie valley to Wuzhang", "第五次北伐：出斜谷屯五丈原",
  "Up the Xie valley road to the Wuzhang plains, a hundred days facing Sima Yi across the Wei.",
  "经褒斜道北出斜谷，屯兵五丈原，与司马懿隔渭水对峙百余日。", [["南郑", "褒谷口", "斜谷口", "五丈原"]]),
 ("liaodong", "cao", 238, 238, "106", "Sima Yi marches on Liaodong", "司马懿远征辽东",
  "Four thousand li from Luoyang to Xiangping.", "司马懿自洛阳远征四千里，直抵襄平。", [["洛阳", "邺", "孤竹", "辽隧", "襄平"]]),
 ("jiang-wei-taoxi", "liu", 255, 255, "110", "Jiang Wei's march to the Tao", "姜维出兵洮西",
  "Jiang Wei's greatest victory, west of the Tao at Didao.", "姜维出兵洮西，大破魏军于狄道。", [["武都", "沓中", "狄道"]]),
 ("jiang-wei-duangu", "liu", 256, 256, "111", "Jiang Wei's march to Duangu", "姜维兵败段谷",
  "Out through Qishan towards Shanggui; Deng Ai is waiting at Duangu.", "姜维出祁山向上邽，被邓艾在段谷击败。",
  [["祁山", "上邽", "段谷"]]),
 ("jiang-wei-luo", "liu", 257, 257, "112", "Jiang Wei through the Luo valley", "姜维出骆谷",
  "Through the Luo valley to the grain stores at Changcheng.", "姜维出骆谷，直逼长城囤粮处。", [["南郑", "骆谷", "长城"]]),
 ("zhong-hui", "cao", 263, 263, "116–117", "Zhong Hui invades through Hanzhong", "钟会伐蜀",
  "A hundred thousand men through the Luo valley into Hanzhong, then south to Jiange, where Jiang Wei holds him.",
  "钟会率十余万大军经骆谷入汉中，南下至剑阁，被姜维挡住。", [["长安", "骆谷", "南郑", "阳平关", "剑阁"]]),
 ("deng-ai", "cao", 263, 263, "117–118", "Deng Ai through the Yinping wilderness", "邓艾偷渡阴平",
  "From Didao against Jiang Wei at Tazhong, then seven hundred li of trackless mountains to Jiangyou, Mianzhu and Chengdu.",
  "邓艾自狄道攻沓中，再穿越七百里无人山区，经江油、绵竹，直取成都。", [["狄道", "沓中", "阴平", "江油", "绵竹", "成都"]]),
 ("jiang-wei-jiange", "liu", 263, 263, "116–117", "Jiang Wei falls back to Jiange", "姜维退守剑阁",
  "From Tazhong past Yinping to the pass at Jiange.", "姜维自沓中经阴平退守剑阁。", [["沓中", "阴平", "剑阁"]]),
 ("wang-jun", "jin", 279, 280, "120", "Wang Jun's fleet comes down the Yangzi", "王濬楼船下益州",
  "From Chengdu down the whole Yangzi, burning the chains across the gorges, to Jianye.", "王濬楼船自成都顺江而下，烧断横江铁锁，直抵建业。",
  [["成都", "江州", "白帝", "西陵", "江陵", "武昌", "建业"]]),
 ("du-yu", "jin", 279, 280, "120", "Du Yu takes Jiangling", "杜预攻取江陵",
  "From Xiangyang south to Jiangling, 'like splitting bamboo'.", "杜预自襄阳南下攻克江陵，势如破竹。", [["襄阳", "江陵"]]),
 ("wang-hun", "jin", 279, 280, "120", "Wang Hun comes down to the river", "王浑进兵江北",
  "From Shouchun to the north bank opposite Jianye.", "王浑自寿春南下，进至建业对岸的江北。", [["寿春", "合肥", "历阳"]]),
]
P["寿春"] = [116.78, 32.57]


def leg(names, cid):
    for n in names:
        assert n in P, f"{cid}: unknown place {n}"
    return [P[n] for n in names]


feats = []
for cid, side, a, b, chs, n, nz, t, tz, legs in CAMPAIGNS:
    color, sn, snz = SIDES[side]
    lines = [leg(l, cid) for l in legs]
    geom = {"type": "LineString", "coordinates": lines[0]} if len(lines) == 1 else {"type": "MultiLineString", "coordinates": lines}
    feats.append({"type": "Feature", "geometry": geom, "properties": {
        "id": cid, "side": side, "color": color, "from": a, "to": b + 1,
        "name": n, "name_zh": nz, "text": f"{sn}, {a}{'–' + str(b) if b != a else ''}, chapters {chs}. {t}",
        "text_zh": f"{snz}，{a}{'–' + str(b) if b != a else ''}年，第{chs}回。{tz}"}})
assert len({f["properties"]["id"] for f in feats}) == len(feats), "duplicate campaign ids"
dump("campaigns", feats)

