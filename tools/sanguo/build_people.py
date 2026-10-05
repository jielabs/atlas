"""Build the Three Kingdoms pack's rulers and people, and link the people to the events that name them.

Usage: python3 tools/sanguo/build_people.py        (writes packs/sanguo/people.json, sets "people" on events.json)

people.json is the pack's `data.people`, in the format of the atlas's per-period files (data/layers/<era>.json):
`polities` and `rulers` (reigns by country) and `people`, for the whole pack; the engine gives each period the reigns
and lives that touch its years. A country whose key is a name on the border maps (Han, Wei, Shu Han, Wu, Jin, The
Gongsun of Liaodong) shows its reigning ruler under that label. The warlords are keyed apart from their labels, which
already carry their names, so they appear in the Rulers tab only.

The novel leads, as in the events: the people are its cast, each placed where the novel most often puts them (people
sharing a place are fanned out a little around it), and what they are known for is what the novel tells, with a
note where history disagrees. Lives are historical. A person's marker shows (`show`) from the first event that names
them, when they come on stage, until their death, or for the years the novel names them if it keeps them alive
longer; a person no event names shows for their life or the years the novel gives them.

Each event gets "people": everyone its Chinese title or summary names, by name or by a by-name the novel uses (孔明,
云长, 阿斗...), in order of first mention. People link to the Wikipedia pages tools/sanguo/fetch_images.py found
(tools/sanguo/wiki_pages.json), shown on their cards.
"""
import ast, json, math, os, re

PACK = "packs/sanguo"
# The novel's places, shared with the army movements (tools/sanguo/build_layers.py), plus a few of the people's own.
P = next(ast.literal_eval(n.value) for n in ast.parse(open("tools/sanguo/build_layers.py", encoding="utf-8").read()).body
         if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "P")
P.update({"涿郡": [115.97, 39.48], "阆中": [105.97, 31.58], "常山": [114.57, 38.15], "隆中": [112.05, 32.0],
          "小沛": [116.93, 34.73], "蓝田": [109.32, 34.15], "谯": [115.78, 33.85], "北海": [118.75, 36.75],
          "郿": [107.75, 34.28], "寿春": [116.78, 32.57], "巨鹿": [115.03, 37.22], "武威": [102.63, 37.93],
          "安汉": [106.08, 30.8]})
PLACE_EN = {
 "涿郡": "Zhuo commandery", "江陵": "Jiangling", "阆中": "Langzhong", "常山": "Changshan", "隆中": "Longzhong",
 "雒": "Luo (Fallen Phoenix Slope)", "新野": "Xinye", "定军山": "Mount Dingjun", "潼关": "Tong Pass", "南郑": "Nanzheng (Hanzhong)",
 "剑阁": "Jiange", "成都": "Chengdu", "街亭": "Jieting", "麦城": "Maicheng", "味县": "Wei county (Nanzhong)",
 "公安": "Gong'an", "长坂": "Changban", "江州": "Jiangzhou (Ba)", "许": "Xu", "洛阳": "Luoyang", "邺": "Ye", "宛": "Wan",
 "五丈原": "Wuzhang Plains", "小沛": "Xiaopei", "樊城": "Fancheng", "合肥": "Hefei", "木门": "Mumen", "阴平": "Yinping",
 "斜谷口": "Xie Valley", "蓝田": "Lantian", "谯": "Qiao", "北海": "Beihai", "祁山": "Mount Qi", "乌林": "Wulin",
 "长沙": "Changsha", "吴": "Wu commandery", "建业": "Jianye", "赤壁": "Red Cliffs", "陆口": "Lukou", "寻阳": "Xunyang",
 "猇亭": "Xiaoting", "濡须": "Ruxu", "曲阿": "Qu'e", "皖": "Wan (Lujiang)", "西陵": "Xiling", "郿": "Mei (his fortress)",
 "下邳": "Xiapi", "长安": "Chang'an", "寿春": "Shouchun", "襄阳": "Xiangyang", "巨鹿": "Julu", "易": "Yijing",
 "武威": "Wuwei", "郯": "Tan", "汜水关": "Sishui Pass", "白马": "Baima", "延津": "Yanjin", "乌巢": "Wuchao",
 "襄平": "Xiangping", "安汉": "Anhan (Nanchong)",
}
PLACE_ZH = {"雒": "雒城落凤坡", "南郑": "汉中南郑", "味县": "南中味县", "江州": "巴郡江州", "许": "许都", "郿": "郿坞",
            "易": "易京", "皖": "庐江皖城", "安汉": "巴西安汉"}

# ---- countries and their rulers -----------------------------------------------------------------------------------
# key: (name_zh, focus, [(name, name_zh, title, title_zh, from, to, circa)])
RULERS = {
 "Han": ("东汉", True, [
  ("Liu Hong", "刘宏", "Emperor Ling of Han", "汉灵帝", 168, 189, False),
  ("Liu Bian", "刘辩", "Emperor Shao of Han", "汉少帝", 189, 189, False),
  ("Liu Xie", "刘协", "Emperor Xian of Han", "汉献帝", 189, 220, False)]),
 "Wei": ("曹魏", True, [
  ("Cao Cao", "曹操", "Duke of Wei", "魏公", 213, 216, False),
  ("Cao Cao", "曹操", "King of Wei (Emperor Wu, posthumously)", "魏王（追尊魏武帝）", 216, 220, False),
  ("Cao Pi", "曹丕", "Emperor Wen of Wei", "魏文帝", 220, 226, False),
  ("Cao Rui", "曹叡", "Emperor Ming of Wei", "魏明帝", 226, 239, False),
  ("Cao Fang", "曹芳", "Prince of Qi", "齐王", 239, 254, False),
  ("Cao Mao", "曹髦", "Duke of Gaogui Village", "高贵乡公", 254, 260, False),
  ("Cao Huan", "曹奂", "Emperor Yuan of Wei", "魏元帝", 260, 265, False)]),
 "Shu Han": ("蜀汉", True, [
  ("Liu Bei", "刘备", "King of Hanzhong", "汉中王", 219, 221, False),
  ("Liu Bei", "刘备", "Emperor Zhaolie of Han", "汉昭烈帝", 221, 223, False),
  ("Liu Shan", "刘禅", "The Later Sovereign", "蜀汉后主", 223, 263, False)]),
 "Wu": ("孙吴", True, [
  ("Sun Quan", "孙权", "King of Wu", "吴王", 221, 229, False),
  ("Sun Quan", "孙权", "Emperor Da of Wu", "吴大帝", 229, 252, False),
  ("Sun Liang", "孙亮", "Prince of Kuaiji", "会稽王", 252, 258, False),
  ("Sun Xiu", "孙休", "Emperor Jing of Wu", "吴景帝", 258, 264, False),
  ("Sun Hao", "孙皓", "Last Emperor of Wu", "吴末帝", 264, 280, False)]),
 "Jin": ("西晋", True, [
  ("Sima Zhao", "司马昭", "Duke of Jin", "晋公", 263, 264, False),
  ("Sima Zhao", "司马昭", "King of Jin (Emperor Wen, posthumously)", "晋王（追尊晋文帝）", 264, 265, False),
  ("Sima Yan", "司马炎", "Emperor Wu of Jin", "晋武帝", 265, 290, False)]),
 "Yellow Turbans": ("黄巾军", False, [
  ("Zhang Jiao", "张角", "General of Heaven", "天公将军", 184, 184, False)]),
 "Dong Zhuo and his generals": ("董卓及其部将", False, [
  ("Dong Zhuo", "董卓", "Chancellor of State", "相国", 189, 192, False),
  ("Li Jue and Guo Si", "李傕、郭汜", "", "", 192, 198, False)]),
 "Yuan of Hebei": ("河北袁氏", False, [
  ("Yuan Shao", "袁绍", "Governor of Ji", "冀州牧", 191, 202, False),
  ("Yuan Shang", "袁尚", "Governor of Ji (against his brother Yuan Tan)", "冀州牧（与兄袁谭相争）", 202, 207, False)]),
 "Yuan Shu": ("袁术", False, [
  ("Yuan Shu", "袁术", "General of the Rear", "后将军", 189, 197, False),
  ("Yuan Shu", "袁术", "Emperor of Zhong", "仲家皇帝", 197, 199, False)]),
 "Xu province": ("徐州", False, [
  ("Tao Qian", "陶谦", "Governor of Xu", "徐州牧", 188, 194, False),
  ("Liu Bei", "刘备", "Governor of Xu", "徐州牧", 194, 196, False),
  ("Lü Bu", "吕布", "Governor of Xu", "徐州牧", 196, 198, False)]),
 "You province": ("幽州", False, [
  ("Liu Yu", "刘虞", "Governor of You", "幽州牧", 188, 193, False),
  ("Gongsun Zan", "公孙瓒", "General of the Van", "前将军", 193, 199, False)]),
 "Jing province": ("荆州", False, [
  ("Liu Biao", "刘表", "Governor of Jing", "荆州牧", 190, 208, False),
  ("Liu Cong", "刘琮", "Governor of Jing", "荆州牧", 208, 208, False)]),
 "Yi province": ("益州", False, [
  ("Liu Yan", "刘焉", "Governor of Yi", "益州牧", 188, 194, False),
  ("Liu Zhang", "刘璋", "Governor of Yi", "益州牧", 194, 214, False)]),
 "Hanzhong": ("汉中", False, [
  ("Zhang Lu", "张鲁", "Lord Master of the Five Pecks of Rice", "五斗米道师君", 191, 215, False)]),
 "Liang province": ("西凉马氏", False, [
  ("Ma Teng", "马腾", "General Who Conquers the West", "征西将军", 187, 208, True),
  ("Ma Chao", "马超", "Commander of the northwest", "西凉军统帅", 208, 214, False)]),
 "Jiangdong": ("江东孙氏", False, [
  ("Sun Jian", "孙坚", "Grand Administrator of Changsha", "长沙太守", 187, 191, False),
  ("Sun Ce", "孙策", "General Who Attacks Rebels", "讨逆将军", 194, 200, False),
  ("Sun Quan", "孙权", "General Who Attacks Caitiffs", "讨虏将军", 200, 221, False)]),
 "The Gongsun of Liaodong": ("辽东公孙氏", False, [
  ("Gongsun Du", "公孙度", "Grand Administrator of Liaodong", "辽东太守", 189, 204, False),
  ("Gongsun Kang", "公孙康", "Grand Administrator of Liaodong", "辽东太守", 204, 221, True),
  ("Gongsun Gong", "公孙恭", "Grand Administrator of Liaodong", "辽东太守", 221, 228, True),
  ("Gongsun Yuan", "公孙渊", "Grand Administrator of Liaodong", "辽东太守", 228, 237, False),
  ("Gongsun Yuan", "公孙渊", "King of Yan", "燕王", 237, 238, False)]),
}

# ---- people ---------------------------------------------------------------------------------------------------------
# (id, name, name_zh, born, died, field, place, by-names, known for (en), known for (zh), show)
# Fields as in the atlas's data/layers people, plus strategist (谋士) and other.
PEOPLE = [
 # Shu
 ("liu-bei", "Liu Bei", "刘备", 161, 223, "statesman", "涿郡", ["玄德", "先主"],
  "A distant kinsman of the Han who sold straw sandals; swore brotherhood in the peach garden, called on Zhuge Liang three times and founded Shu Han.",
  "织席贩履的汉室宗亲，桃园结义起兵，三顾茅庐请出诸葛亮，建立蜀汉。", None),
 ("guan-yu", "Guan Yu", "关羽", None, 220, "general", "江陵", ["云长", "关公", "美髯公"],
  "The Lord of the Beautiful Beard: slew Hua Xiong and Yan Liang, rode through five passes, held Jingzhou and lost it; worshipped later as a god of war.",
  "美髯公，温酒斩华雄、斩颜良、过五关、单刀赴会、水淹七军，终因大意失荆州败走麦城，后世奉为武圣。", None),
 ("zhang-fei", "Zhang Fei", "张飞", None, 221, "general", "阆中", ["翼德", "益德"],
  "Zhang Yide of Yan, whose roar on the bridge at Changban held back Cao Cao's army; murdered by his own men before he could avenge Guan Yu.",
  "燕人张翼德，长坂桥上一声断喝喝退曹军，义释严颜；为关羽报仇出兵前被部将刺杀。", None),
 ("zhao-yun", "Zhao Yun", "赵云", None, 229, "general", "常山", ["子龙"],
  "Zhao Zilong of Changshan, who rode through Cao Cao's army at Changban with Liu Bei's infant son, and in the novel still takes the field at seventy.",
  "常山赵子龙，长坂坡单骑救阿斗，截江夺斗，汉水空营退曹军，演义写他七十岁仍出阵。", None),
 ("zhuge-liang", "Zhuge Liang", "诸葛亮", 181, 234, "strategist", "隆中", ["孔明", "卧龙"],
  "The Sleeping Dragon: planned the three-way division of the realm, allied with Wu against Cao Cao, ran Shu Han for Liu Bei and his son, and died on campaign at Wuzhang Plains. The novel makes him a wizard.",
  "卧龙，隆中对定三分天下之策，联吴抗曹，辅佐刘备父子治蜀，七擒孟获，六出祁山，病逝五丈原；演义把他写成神机妙算的化身。", None),
 ("pang-tong", "Pang Tong", "庞统", 179, 214, "strategist", "雒", ["士元", "凤雏"],
  "The Fledgling Phoenix, Zhuge Liang's equal; in the novel he talks Cao Cao into chaining his ships, and dies under arrows at Fallen Phoenix Slope (historically, a stray arrow at the siege of Luo).",
  "凤雏，与卧龙齐名；演义写他向曹操献连环计（虚构），入川途中在落凤坡中箭身亡（史实是围雒城时中流矢）。", None),
 ("xu-shu", "Xu Shu", "徐庶", None, None, "strategist", "新野", ["单福", "元直"],
  "Liu Bei's first strategist, under the name Shan Fu; when Cao Cao held his mother he left, recommending Zhuge Liang as he rode away.",
  "化名单福，为刘备出谋大破曹仁；因母亲被曹操扣押而离去，临行走马荐诸葛。", [196, 230]),
 ("fa-zheng", "Fa Zheng", "法正", 176, 220, "strategist", "定军山", ["孝直"],
  "Liu Zhang's officer who brought Liu Bei into Shu, and planned the Hanzhong campaign in which Huang Zhong killed Xiahou Yuan.",
  "迎刘备入川的内应，汉中之战为黄忠定计斩夏侯渊。", None),
 ("ma-chao", "Ma Chao", "马超", 176, 222, "general", "潼关", ["孟起"],
  "Splendid Ma Chao, who rose to avenge his father and at Tong Pass sent Cao Cao fleeing without beard or cloak (historically he rebelled first, and his father was executed for it); later one of Liu Bei's five tiger generals.",
  "锦马超，起兵为父报仇（史实是他先反，马腾因此被杀），潼关之战杀得曹操割须弃袍；后归刘备，为五虎上将之一。", None),
 ("huang-zhong", "Huang Zhong", "黄忠", None, 220, "general", "定军山", ["汉升"],
  "The old general who cut down Xiahou Yuan at Mount Dingjun; one of the five tiger generals.",
  "老当益壮，定军山斩夏侯渊，五虎上将之一。", None),
 ("wei-yan", "Wei Yan", "魏延", None, 234, "general", "南郑", ["文长"],
  "Held Hanzhong for Shu for fifteen years; his plan to strike through the Ziwu Valley was refused, and after Zhuge Liang's death he fell in a feud with Yang Yi. The novel gives him a rebel's bone.",
  "镇守汉中十五年，子午谷奇谋未被采纳；诸葛亮死后与杨仪争权，被马岱斩杀。演义说他'脑后有反骨'。", None),
 ("jiang-wei", "Jiang Wei", "姜维", 202, 264, "general", "剑阁", ["伯约"],
  "Zhuge Liang's heir in war, who marched north again and again and held Jiange; after Shu surrendered he plotted with Zhong Hui to restore it, and died in the attempt.",
  "诸葛亮的衣钵传人，九伐中原，据守剑阁；蜀亡后假意降钟会图谋复国，事败身死。", None),
 ("liu-shan", "Liu Shan", "刘禅", 207, 271, "statesman", "成都", ["阿斗", "后主"],
  "A Dou, the Later Sovereign, who reigned forty-one years; a captive in Luoyang after the surrender, he said he was too happy there to miss Shu.",
  "阿斗，蜀汉后主，在位四十一年；降魏后在洛阳说出'此间乐，不思蜀'。", None),
 ("ma-su", "Ma Su", "马谡", 190, 228, "general", "街亭", ["幼常"],
  "Talked brilliantly of war and lost the crossroads of Jieting; Zhuge Liang executed him in tears.",
  "好论军计，失守街亭，被诸葛亮挥泪斩首。", None),
 ("guan-ping", "Guan Ping", "关平", None, 220, "general", "麦城", [],
  "Guan Yu's son (the novel makes him adopted), captured and killed with his father after Maicheng.",
  "关羽之子（演义作义子），随父败走麦城，一同被擒遇害。", [200, 220]),
 ("zhou-cang", "Zhou Cang", "周仓", None, None, "general", "麦城", [],
  "Invented: the black-faced giant who carries Guan Yu's glaive, and cuts his own throat at Maicheng when Guan Yu falls.",
  "虚构人物：为关羽扛青龙偃月刀的黑脸大汉，关羽死后在麦城自刎。", [190, 220]),
 ("meng-huo", "Meng Huo", "孟获", None, None, "general", "味县", [],
  "A Nanzhong chieftain whom Zhuge Liang captured seven times and released seven times, until he swore loyalty (the seven captures come only from a later source).",
  "南中豪帅，被诸葛亮七擒七纵，终于心服归顺（七擒之说只见于裴注引《汉晋春秋》）。", [220, 240]),
 ("jiang-wan", "Jiang Wan", "蒋琬", None, 246, "statesman", "成都", ["公琰"],
  "Zhuge Liang's chosen successor, who led the Shu government after him.",
  "诸葛亮指定的继任者，诸葛亮死后主持蜀汉国政。", None),
 ("lady-sun", "Lady Sun", "孙夫人", None, None, "other", "公安", ["孙尚香"],
  "Sun Quan's sister, married to Liu Bei in the novel's comic match at Ganlu Temple and taken back to Wu; the name Sun Shangxiang comes from later opera.",
  "孙权之妹，甘露寺招亲嫁给刘备，后被孙权接回东吴；'孙尚香'之名出自后世戏曲。", [200, 223]),
 ("lady-mi", "Lady Mi", "糜夫人", None, None, "other", "长坂", [],
  "Liu Bei's wife who, in the novel, gives his son to Zhao Yun at Changban and throws herself into a well (the histories are silent).",
  "刘备之妻；演义写她在长坂坡把阿斗托付给赵云后投井而死（史书未载）。", [196, 208]),
 ("yan-yan", "Yan Yan", "严颜", None, None, "general", "江州", [],
  "The old general of Ba who would rather lose his head than surrender; Zhang Fei, struck by his courage, set him free.",
  "巴郡老将，'但有断头将军，无有降将军'，张飞敬其义而释之。", [200, 220]),
 # Wei
 ("cao-cao", "Cao Cao", "曹操", 155, 220, "statesman", "许", ["孟德", "曹公", "阿瞒"],
  "'An able minister in peace, a villain in chaos': held the emperor in his hand, beat Yuan Shao at Guandu, united the north and lost at the Red Cliffs. The novel makes him the villain; history also knows him as a poet and reformer.",
  "'治世之能臣，乱世之奸雄'：挟天子以令诸侯，官渡破袁绍，统一北方，赤壁败北。演义把他写成奸雄，史书中他也是诗人和改革者。", None),
 ("cao-pi", "Cao Pi", "曹丕", 187, 226, "statesman", "洛阳", ["魏文帝", "子桓"],
  "Cao Cao's heir, who made the last Han emperor abdicate and founded Wei as its Emperor Wen; also a poet and critic.",
  "曹操之子，逼汉献帝禅让建立魏朝，是为魏文帝；也是诗人和文论家。", None),
 ("cao-zhi", "Cao Zhi", "曹植", 192, 232, "poet", "邺", ["子建"],
  "The finest poet of the age, author of the Nymph of the Luo; the poem made in seven paces is a later legend.",
  "才高八斗，《洛神赋》作者；'七步成诗'出自《世说新语》的传说。", None),
 ("xun-yu", "Xun Yu", "荀彧", 163, 212, "strategist", "许", ["文若"],
  "Cao Cao's chief counsellor, who urged him to take in the emperor and hold firm at Guandu; he opposed Cao Cao's rise to duke and died soon after (in the novel, on receiving an empty food box).",
  "曹操首席谋臣，力主迎献帝、官渡坚守；反对曹操称魏公，不久忧死（演义说收到空食盒后服毒）。", None),
 ("guo-jia", "Guo Jia", "郭嘉", 170, 207, "strategist", "许", ["奉孝"],
  "Cao Cao's brilliant young strategist, whose last plan won Liaodong; after the Red Cliffs Cao Cao wept that had he lived, the defeat would not have happened.",
  "曹操的'鬼才'谋士，遗计定辽东；赤壁败后曹操大哭'若奉孝在，决不使吾有此大失'。", None),
 ("jia-xu", "Jia Xu", "贾诩", 147, 223, "strategist", "宛", ["文和"],
  "The coldest strategist of the age: told Li Jue and Guo Si to retake Chang'an, helped Zhang Xiu beat Cao Cao twice, then served Cao Cao and split Ma Chao from Han Sui.",
  "毒士，劝李傕、郭汜反攻长安，助张绣两败曹操，归曹后献计离间马超、韩遂。", None),
 ("sima-yi", "Sima Yi", "司马懿", 179, 251, "strategist", "五丈原", ["仲达", "司马宣王"],
  "Wei's great general and Zhuge Liang's patient opponent, scared off by the empty fort in the novel; his coup of 249 put Wei in his family's hands.",
  "魏国重臣，诸葛亮北伐的老对手，演义中被空城计吓退；249年高平陵之变后司马氏掌控魏国。", None),
 ("xiahou-dun", "Xiahou Dun", "夏侯惇", None, 220, "general", "小沛", ["元让"],
  "Cao Cao's kinsman and general, who in the novel pulls an arrow from his eye and swallows the eye.",
  "曹操宗族大将，演义写他中箭后'拔矢啖睛'；博望坡中诸葛亮火攻。", None),
 ("xiahou-yuan", "Xiahou Yuan", "夏侯渊", None, 219, "general", "定军山", ["妙才"],
  "Cao Cao's swift kinsman who held the west, killed by Huang Zhong at Mount Dingjun.",
  "曹操宗族名将，镇守西方，定军山被黄忠斩杀。", None),
 ("cao-ren", "Cao Ren", "曹仁", 168, 223, "general", "樊城", [],
  "Cao Cao's cousin, who held Fancheng against Guan Yu through the flood.",
  "曹操族弟，镇守樊城，关羽水淹七军时坚守待援。", None),
 ("zhang-liao", "Zhang Liao", "张辽", 169, 222, "general", "合肥", ["文远"],
  "Charged Sun Quan's army at Xiaoyao Ford with eight hundred men; in Wu, children were hushed with his name.",
  "逍遥津八百人冲破孙权大军，威震江东，'小儿止啼'。", None),
 ("xu-huang", "Xu Huang", "徐晃", None, 227, "general", "樊城", ["公明"],
  "Broke Guan Yu's siege lines and relieved Fancheng.",
  "长驱直入，大破关羽，解樊城之围。", None),
 ("zhang-he", "Zhang He", "张郃", None, 231, "general", "木门", ["儁乂"],
  "Went over to Cao Cao at Guandu, beat Ma Su at Jieting, and died in an ambush at Mumen.",
  "官渡降曹，街亭大破马谡，木门道中伏身亡。", None),
 ("dian-wei", "Dian Wei", "典韦", None, 197, "general", "宛", [],
  "Cao Cao's bodyguard, who held the camp gate alone at Wan so that his lord could escape.",
  "曹操贴身护卫，宛城死守营门，掩护曹操逃生。", None),
 ("xu-chu", "Xu Chu", "许褚", None, None, "general", "潼关", ["仲康", "虎痴"],
  "The Tiger Fool, Cao Cao's guard, who fought Ma Chao stripped to the waist.",
  "虎痴，曹操护卫，潼关裸衣斗马超。", [190, 230]),
 ("pang-de", "Pang De", "庞德", None, 219, "general", "樊城", ["令明"],
  "Brought his own coffin to the battle with Guan Yu, and died rather than surrender.",
  "抬棺决战关羽，兵败被擒，宁死不降。", None),
 ("yu-jin", "Yu Jin", "于禁", None, 221, "general", "樊城", [],
  "One of Cao Cao's best generals, who surrendered to Guan Yu when the Han river drowned his seven armies.",
  "曹操名将，汉水泛滥七军被淹，向关羽投降，晚节不保。", None),
 ("deng-ai", "Deng Ai", "邓艾", 197, 264, "general", "阴平", ["士载"],
  "Led his army through the wilds of Yinping to take Chengdu and end Shu; arrested soon after on Zhong Hui's charges, and killed.",
  "偷渡阴平，直取成都，灭蜀首功；旋即被钟会诬告，遇害。", None),
 ("zhong-hui", "Zhong Hui", "钟会", 225, 264, "general", "成都", ["士季"],
  "Led Wei's main army against Shu and was held at Jiange; after the conquest he plotted with Jiang Wei to rule Shu himself, and was killed by his own troops.",
  "统率伐蜀主力，被阻剑阁；灭蜀后与姜维合谋据蜀自立，被乱兵所杀。", None),
 ("sima-zhao", "Sima Zhao", "司马昭", 211, 265, "statesman", "洛阳", [],
  "'Everyone in the street knows what Sima Zhao has in mind': his men killed the emperor Cao Mao, he conquered Shu, and was made King of Jin.",
  "'司马昭之心，路人皆知'：部下弑杀魏帝曹髦，他灭蜀后封晋王。", None),
 ("sima-yan", "Sima Yan", "司马炎", 236, 290, "statesman", "洛阳", ["晋武帝"],
  "Took the throne from Wei as the first Jin emperor, and in 280 conquered Wu: the three kingdoms became one.",
  "受魏禅建立晋朝，280年灭吴，三分归一统。", None),
 ("yang-xiu", "Yang Xiu", "杨修", 175, 219, "scholar", "斜谷口", ["德祖"],
  "Too clever for his own good: he guessed what Cao Cao meant by 'chicken rib' and was put to death.",
  "聪明外露，猜中曹操'鸡肋'之意，被曹操以扰乱军心之名处死。", None),
 ("cai-yan", "Cai Yan", "蔡琰", None, None, "poet", "蓝田", ["蔡文姬", "文姬"],
  "Cai Yong's daughter, twelve years a captive among the Xiongnu until Cao Cao ransomed her; the Eighteen Songs of a Nomad Flute are ascribed to her.",
  "蔡邕之女，流落南匈奴十二年，被曹操重金赎回；相传作《胡笳十八拍》。", [190, 220]),
 ("hua-tuo", "Hua Tuo", "华佗", None, 208, "physician", "谯", ["元化"],
  "The divine physician, who in the novel scrapes the poison from Guan Yu's bone, and dies for offering to open Cao Cao's skull.",
  "神医；演义写他为关羽刮骨疗毒，又因提议为曹操开颅治头风被杀。", None),
 ("kong-rong", "Kong Rong", "孔融", 153, 208, "writer", "北海", ["文举"],
  "A descendant of Confucius, the boy who took the smaller pear; executed for mocking Cao Cao.",
  "孔子后裔，'孔融让梨'的主角，北海太守，因屡屡讥讽曹操被杀。", None),
 ("mi-heng", "Mi Heng", "祢衡", 173, 198, "writer", "许", [],
  "Stripped and beat out an insult to Cao Cao on a drum; passed from patron to patron until Huang Zu killed him.",
  "击鼓骂曹，被辗转送往刘表、黄祖处，终被黄祖所杀。", None),
 ("chen-lin", "Chen Lin", "陈琳", None, 217, "writer", "邺", ["孔璋"],
  "Wrote Yuan Shao's denunciation of Cao Cao, so fierce it was said to cure Cao Cao's headache; Cao Cao spared him for his pen.",
  "为袁绍写讨曹檄文，据说吓得曹操头风都好了；袁绍败后曹操爱其才而赦之。", None),
 ("zuo-ci", "Zuo Ci", "左慈", None, None, "religious", "邺", ["元放"],
  "A Daoist magician who mocks Cao Cao with conjuring at his banquet.",
  "方士，在曹操宴上变戏法戏弄曹操（演义据《后汉书·方术传》）。", [195, 220]),
 ("wang-lang", "Wang Lang", "王朗", None, 228, "statesman", "祁山", ["景兴"],
  "Wei minister whom, in the novel, Zhuge Liang scolds to death before the armies (invented; he died at home the same year).",
  "魏国重臣；演义写他在阵前被诸葛亮骂死（虚构，史实是同年病逝）。", None),
 ("cai-mao", "Cai Mao", "蔡瑁", None, None, "general", "乌林", ["德珪"],
  "Liu Biao's admiral who went over to Cao Cao; the novel has Cao Cao behead him, fooled by a letter Zhou Yu forged (invented).",
  "刘表的水军都督，降曹；演义写曹操中周瑜反间计将其斩首（虚构）。", [190, 208]),
 ("jiang-gan", "Jiang Gan", "蒋干", None, None, "statesman", "乌林", ["子翼"],
  "Cao Cao's envoy to his old schoolmate Zhou Yu, who in the novel steals a forged letter and gets Cao Cao's admirals killed.",
  "曹操派去劝降周瑜的同窗；演义写他群英会上盗走伪造的书信，害死蔡瑁、张允。", [200, 220]),
 ("emperor-xian", "Emperor Xian of Han", "汉献帝", 181, 234, "statesman", "许", ["献帝", "刘协"],
  "The last Han emperor, a pawn of Dong Zhuo, Li Jue and Cao Cao; his secret edict sewn into a belt failed, and in 220 he gave the throne to Cao Pi.",
  "东汉末代皇帝，先后受制于董卓、李傕、曹操；衣带诏事泄，220年禅位于曹丕。", None),
 # Wu
 ("sun-jian", "Sun Jian", "孙坚", 155, 191, "general", "长沙", ["文台"],
  "The Tiger of Jiangdong: vanguard against Dong Zhuo, finder of the imperial seal in Luoyang, killed in an ambush fighting Liu Biao.",
  "江东猛虎，讨董先锋，在洛阳得传国玉玺，攻刘表时中伏身亡。", None),
 ("sun-ce", "Sun Ce", "孙策", 175, 200, "general", "吴", ["伯符", "小霸王"],
  "The Little Conqueror, who won the lands south of the Yangtze in a few years and died at twenty-five, haunted (says the novel) by the Daoist Yu Ji.",
  "小霸王，数年间平定江东；遇刺伤重，二十六岁去世，演义说他是被于吉的鬼魂所扰。", None),
 ("sun-quan", "Sun Quan", "孙权", 182, 252, "statesman", "建业", ["仲谋"],
  "Inherited Jiangdong at eighteen, allied with Liu Bei to beat Cao Cao at the Red Cliffs, took Jingzhou from Guan Yu, beat Liu Bei at Yiling and made himself emperor of Wu.",
  "十八岁继承江东，联刘抗曹赤壁破敌，袭取荆州，夷陵败刘备，称帝建立吴国。", None),
 ("zhou-yu", "Zhou Yu", "周瑜", 175, 210, "general", "赤壁", ["公瑾", "周郎"],
  "Handsome Zhou, commander at the Red Cliffs; the novel makes him jealous of Zhuge Liang, who angers him to death three times over, though history calls him generous.",
  "美周郎，赤壁之战主帅；演义写他气量狭小，被诸葛亮'三气'而死，史书却称他'性度恢廓'。", None),
 ("lu-su", "Lu Su", "鲁肃", 172, 217, "strategist", "陆口", ["子敬"],
  "Wu's champion of the alliance with Liu Bei; the novel makes him an honest dupe, though at the 'single sword meeting' it was he who faced down Guan Yu.",
  "力主孙刘联盟；演义把他写成被诸葛亮牵着走的老实人，其实'单刀会'上是他当面诘责关羽。", None),
 ("lu-meng", "Lü Meng", "吕蒙", 178, 220, "general", "寻阳", ["子明", "阿蒙"],
  "The soldier who took up books ('no longer the Lü Meng of Wu'); hid his men in merchant boats, dressed in white, to take Jingzhou from Guan Yu.",
  "'士别三日，刮目相待'，白衣渡江袭取荆州，擒杀关羽。", None),
 ("lu-xun", "Lu Xun", "陆逊", 183, 245, "general", "猇亭", ["伯言"],
  "A young scholar made commander, who burned Liu Bei's line of camps at Yiling.",
  "书生拜将，夷陵之战火烧连营，大败刘备。", None),
 ("huang-gai", "Huang Gai", "黄盖", None, None, "general", "赤壁", ["公覆"],
  "Took a flogging to make his false surrender believable, then sailed the fire ships into Cao Cao's fleet at the Red Cliffs.",
  "苦肉计受杖诈降，赤壁之战驾火船冲入曹军水寨。", [184, 215]),
 ("gan-ning", "Gan Ning", "甘宁", None, None, "general", "濡须", ["兴霸"],
  "A river pirate turned general, who raided Cao Cao's camp at Ruxu with a hundred horsemen.",
  "锦帆贼出身，濡须口百骑劫魏营。", [195, 220]),
 ("taishi-ci", "Taishi Ci", "太史慈", 166, 206, "general", "曲阿", [],
  "Fought Sun Ce to a standstill at Shenting, then became his general.",
  "神亭岭与孙策酣斗，后归顺孙策。", None),
 ("zhang-zhao", "Zhang Zhao", "张昭", 156, 236, "statesman", "建业", ["子布"],
  "Sun Ce's chief minister and Sun Quan's guardian, who argued for surrender to Cao Cao before the Red Cliffs.",
  "孙策托孤重臣，赤壁之战前力主降曹。", None),
 ("qiao-sisters", "The Qiao sisters", "大乔、小乔", None, None, "other", "皖", ["大乔", "小乔", "二乔"],
  "The two beauties of Jiangdong: the elder married Sun Ce, the younger Zhou Yu. The novel has Zhuge Liang goad Zhou Yu by claiming Cao Cao wanted them for his Bronze Bird Terrace.",
  "江东二乔：大乔嫁孙策，小乔嫁周瑜；演义写诸葛亮称曹操欲得二乔置于铜雀台，激怒周瑜。", [199, 220]),
 ("lu-kang", "Lu Kang", "陆抗", 226, 274, "general", "西陵", ["幼节"],
  "Lu Xun's son, who held the Jingzhou frontier against Yang Hu; the two enemies sent each other wine and medicine.",
  "陆逊之子，与晋将羊祜对峙荆州边境，互赠酒药，传为'羊陆之交'。", None),
 ("sun-hao", "Sun Hao", "孙皓", 242, 284, "statesman", "建业", [],
  "Wu's cruel last emperor, who surrendered with his hands bound when the Jin fleets reached Jianye in 280.",
  "东吴末帝，暴虐无道；280年晋军顺江而下兵临建业，他面缚出降。", None),
 ("yu-ji", "Yu Ji", "于吉", None, 200, "religious", "吴", [],
  "A Daoist healer whom Sun Ce put to death; the novel has his ghost haunt Sun Ce to the grave.",
  "道士，被孙策以惑众之名处死；演义写他的鬼魂纠缠孙策至死（出自《搜神记》等）。", None),
 # The others
 ("dong-zhuo", "Dong Zhuo", "董卓", None, 192, "general", "郿", [],
  "The northwestern general who seized the capital, put one emperor in place of another, burned Luoyang and dragged the court to Chang'an, until Lü Bu killed him.",
  "西凉军阀，入京废少帝立献帝，焚洛阳、迁长安，暴虐无道，被吕布所杀。", None),
 ("lu-bu", "Lü Bu", "吕布", None, 199, "general", "下邳", ["奉先"],
  "'Among men Lü Bu, among horses Red Hare': the finest fighter of the age, who killed two masters, shot the halberd at the camp gate, and was strangled at White Gate Tower.",
  "'人中吕布，马中赤兔'，先后杀丁原、董卓，辕门射戟，终在下邳白门楼被缢杀。", None),
 ("diao-chan", "Diao Chan", "貂蝉", None, None, "other", "长安", [],
  "Invented (the histories mention only a maid of Dong Zhuo's who had an affair with Lü Bu): in Wang Yun's chain plot she sets Dong Zhuo and Lü Bu against each other.",
  "虚构人物（史书只说吕布与董卓侍婢私通）：王允连环计中周旋于董卓、吕布之间，使二人反目。", [189, 198]),
 ("wang-yun", "Wang Yun", "王允", 137, 192, "statesman", "长安", [],
  "The minister who plotted Dong Zhuo's death; killed when Dong Zhuo's generals took Chang'an.",
  "司徒，设计诛杀董卓；李傕、郭汜攻破长安后遇害。", None),
 ("yuan-shao", "Yuan Shao", "袁绍", None, 202, "statesman", "邺", ["本初"],
  "Of a family with four generations of high ministers; leader of the coalition against Dong Zhuo and master of the north, until Cao Cao beat him at Guandu.",
  "四世三公，讨董盟主，雄踞河北，官渡之战败于曹操，忧愤而死。", None),
 ("yuan-shu", "Yuan Shu", "袁术", None, 199, "statesman", "寿春", [],
  "Proclaimed himself emperor at Shouchun, was abandoned by all, and died vomiting blood, begging for honeyed water.",
  "在寿春称帝，众叛亲离，临终求蜜水而不得，吐血而死。", None),
 ("liu-biao", "Liu Biao", "刘表", 142, 208, "statesman", "襄阳", ["景升"],
  "Governor of Jingzhou, who kept his province out of the wars; after his death his son surrendered to Cao Cao.",
  "荆州牧，坐保江汉；死后其子刘琮举州降曹。", None),
 ("liu-zhang", "Liu Zhang", "刘璋", None, 220, "statesman", "成都", ["季玉"],
  "The weak governor of Yi province, who invited Liu Bei in against Zhang Lu and lost his province to him.",
  "暗弱的益州牧，请刘备入川抵御张鲁，反被刘备夺去益州。", None),
 ("zhang-lu", "Zhang Lu", "张鲁", None, 216, "religious", "南郑", [],
  "Master of the Five Pecks of Rice, who ruled Hanzhong as a church-state for nearly thirty years before submitting to Cao Cao.",
  "五斗米道师君，以政教合一统治汉中近三十年，后降曹操。", None),
 ("zhang-jiao", "Zhang Jiao", "张角", None, 184, "religious", "巨鹿", [],
  "Leader of the Way of Great Peace, who raised the Yellow Turbans with 'the blue heaven is dead, the yellow heaven shall rise', and died of illness that same year.",
  "太平道首领，以'苍天已死，黄天当立'发动黄巾起义，当年病死。", None),
 ("gongsun-zan", "Gongsun Zan", "公孙瓒", None, 199, "general", "易", ["伯珪"],
  "The White Horse General of the north, beaten by Yuan Shao, who burned himself in his tower at Yijing.",
  "白马将军，界桥败于袁绍，困守易京，最后自焚而死。", None),
 ("ma-teng", "Ma Teng", "马腾", None, 212, "general", "武威", ["寿成"],
  "The northwestern warlord, Ma Chao's father; the novel has him killed for joining the plot of the belt edict (historically, for Ma Chao's rising).",
  "西凉军阀，马超之父；演义写他参与衣带诏谋曹被诱杀（史实是马超起兵后他在邺城被杀）。", None),
 ("tao-qian", "Tao Qian", "陶谦", 132, 194, "statesman", "郯", ["恭祖"],
  "Governor of Xu province, who on his deathbed left it to Liu Bei; the novel has him offer it three times.",
  "徐州牧，临终将徐州让给刘备（演义写成'三让徐州'）。", None),
 ("he-jin", "He Jin", "何进", None, 189, "statesman", "洛阳", [],
  "Grand General and the empress's brother, who called Dong Zhuo to the capital to destroy the eunuchs and was murdered by them first.",
  "大将军，何皇后之兄，召董卓进京诛宦官，反被十常侍抢先杀害。", None),
 ("sima-hui", "Sima Hui", "司马徽", None, 208, "scholar", "襄阳", ["水镜", "德操"],
  "Mr Water Mirror, the recluse who told Liu Bei that with either the Sleeping Dragon or the Fledgling Phoenix he could win the realm.",
  "水镜先生，告诉刘备'伏龙、凤雏，两人得一，可安天下'。", None),
 ("hua-xiong", "Hua Xiong", "华雄", None, 191, "general", "汜水关", [],
  "Dong Zhuo's champion, whom Guan Yu kills before his cup of wine grows cold (historically, Sun Jian's army killed him).",
  "董卓骁将；演义写关羽温酒斩华雄，史实是死于孙坚之手。", None),
 ("yan-liang", "Yan Liang", "颜良", None, 200, "general", "白马", [],
  "Yuan Shao's champion, cut down by Guan Yu in the midst of his army at Baima.",
  "袁绍大将，白马之战被关羽于万军之中刺杀。", None),
 ("wen-chou", "Wen Chou", "文丑", None, 200, "general", "延津", [],
  "Yuan Shao's other champion, killed at Yanjin (by Guan Yu, says the novel).",
  "袁绍大将，延津之战被杀（演义说是关羽所斩）。", None),
 ("chen-gong", "Chen Gong", "陈宫", None, 199, "strategist", "下邳", ["公台"],
  "Freed Cao Cao when he was a fugitive, left him in disgust, served Lü Bu, and refused to be spared at White Gate Tower.",
  "捉放曹后弃曹而去，辅佐吕布，白门楼宁死不降。", None),
 ("xu-you", "Xu You", "许攸", None, 204, "strategist", "乌巢", ["子远"],
  "Yuan Shao's adviser who deserted to Cao Cao at Guandu and told him where Yuan's grain lay at Wuchao.",
  "袁绍谋士，官渡之战投曹，献计火烧乌巢粮仓。", None),
 ("gongsun-yuan", "Gongsun Yuan", "公孙渊", None, 238, "general", "襄平", [],
  "Lord of Liaodong who named himself King of Yan; destroyed by Sima Yi in 238.",
  "辽东割据者，自立为燕王，238年被司马懿讨灭。", None),
 ("yang-hu", "Yang Hu", "羊祜", 221, 278, "general", "襄阳", [],
  "Jin's commander in Jingzhou, who won the frontier with kindness and on his deathbed planned the conquest of Wu.",
  "晋朝镇守荆州的统帅，以德怀柔边民，临终举荐杜预，定下灭吴之策。", None),
 ("du-yu", "Du Yu", "杜预", 222, 285, "general", "江陵", ["元凯"],
  "A commander in the conquest of Wu, who said the war would go 'like splitting bamboo'.",
  "灭吴主将之一，'势如破竹'的出处。", None),
 ("wang-jun", "Wang Jun", "王濬", 206, 286, "general", "成都", [],
  "Built the great fleet in Shu that sailed down the Yangtze, burned Wu's iron chains and took Sun Hao's surrender at Jianye.",
  "在蜀地督造楼船，顺江而下烧断吴人铁锁，在建业受孙皓投降。", None),
 ("chen-shou", "Chen Shou", "陈寿", 233, 297, "historian", "安汉", [],
  "A Shu official who, under Jin, wrote the Records of the Three Kingdoms, the history the novel draws on most.",
  "蜀汉旧臣，入晋后撰《三国志》，是《三国演义》最主要的史料来源。", None),
]
# Names that must not match inside a longer one: 庞德公 (Pang Tong's uncle) is not Pang De; 吴后主 is not Liu Shan.
GUARD = {"庞德": r"庞德(?!公)", "后主": r"(?<!吴)后主"}


def fan(people):
    """People who share a place are set around it on a small circle, so each marker can show."""
    at = {}
    for p in people:
        at.setdefault(p["place_zh"], []).append(p)
    for group in at.values():
        if len(group) < 2:
            continue
        for i, p in enumerate(group):
            a = 2 * math.pi * i / len(group)
            p["lon"] = round(p["lon"] + 0.14 * math.cos(a), 3)
            p["lat"] = round(p["lat"] + 0.11 * math.sin(a), 3)


def build():
    # Link the events: a person is named by their name or any of their by-names (a pair like 大乔、小乔 by its parts).
    pats = []
    for pid, name, zh, *_, aka, en, kz, show in PEOPLE:
        names = ([] if "、" in zh else [zh]) + aka
        pats.append((pid, re.compile("|".join(GUARD.get(n, re.escape(n)) for n in names))))
    events = json.load(open(f"{PACK}/events.json", encoding="utf-8"))
    linked, first, last = {}, {}, {}
    for ev in events:
        text = ev["title_zh"] + " " + ev["summary_zh"]
        found = sorted((m.start(), pid) for pid, rx in pats if (m := rx.search(text)))
        ev.pop("people", None)
        if found:
            ev["people"] = [pid for _, pid in found]
            for pid in ev["people"]:
                linked[pid] = linked.get(pid, 0) + 1
                first[pid] = min(first.get(pid, ev["year"]), ev["year"])
                last[pid] = max(last.get(pid, ev["year"]), ev["year"])
    with open(f"{PACK}/events.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(events, ensure_ascii=False, indent=1) + "\n")
    print(f"events.json: {sum(1 for e in events if e.get('people'))} of {len(events)} events name someone; "
          f"{len(linked)} of {len(PEOPLE)} people are named")
    lone = [p[0] for p in PEOPLE if p[0] not in linked]
    if lone:
        print("  named by no event:", ", ".join(lone))

    polities, rulers = {}, {}
    for key, (zh, focus, reigns) in RULERS.items():
        polities[key] = {"name_zh": zh, **({"focus": True} if focus else {})}
        rulers[key] = [{"name": n, "name_zh": nz, **({"title": t, "title_zh": tz} if t else {}), "from": a, "to": b,
                        **({"circa": True} if c else {})} for n, nz, t, tz, a, b, c in reigns]
    wiki = json.load(open("tools/sanguo/wiki_pages.json", encoding="utf-8")) if os.path.exists("tools/sanguo/wiki_pages.json") else {}
    people = []
    for pid, name, zh, born, died, field, place, aka, en, kz, show in PEOPLE:
        lon, lat = P[place]
        p = {"id": pid, "name": name, "name_zh": zh}
        if born is not None: p["born"] = born
        if died is not None: p["died"] = died
        # On stage from the first event that names them (not before birth: a historical note may cite them early).
        # The novel keeps a few alive past their death (Hua Tuo at Guan Yu's arm in 219); they show in its years.
        if pid in first:
            a, b = max(first[pid], born if born is not None else first[pid]), died if died is not None else show[1]
            show = [a, b] if a <= b else [first[pid], last[pid]]
        if show: p["show"] = show
        p.update(field=field, place=PLACE_EN[place], place_zh=PLACE_ZH.get(place, place), lat=lat, lon=lon,
                 known_for=en, known_for_zh=kz)
        for k, w in (("source", "en"), ("source_zh", "zh")):
            if wiki.get(f"p:{pid}", {}).get(w):
                p[k] = wiki[f"p:{pid}"][w]
        people.append(p)
    fan(people)
    with open(f"{PACK}/people.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({"polities": polities, "rulers": rulers, "people": people}, ensure_ascii=False, indent=1) + "\n")
    print(f"people.json: {len(rulers)} countries, {sum(map(len, rulers.values()))} reigns, {len(people)} people")


if __name__ == "__main__":
    build()
