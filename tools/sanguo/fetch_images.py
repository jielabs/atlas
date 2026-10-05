"""Fetch Wikipedia pictures and links for the Three Kingdoms pack's people and main events.

Usage: python3 tools/sanguo/fetch_images.py        (needs Pillow and access to Wikipedia; then run build_people.py)

Each person, and each event that has a page of its own, is matched to an English and a Chinese Wikipedia page
(PEOPLE_EN / PEOPLE_ZH for names that need a qualifier, EVENTS below). The lead image of the English page is taken,
or failing that of the Chinese one, if its licence is free (public domain or Creative Commons; fair-use files are
skipped), shrunk to 320x280 and stored as WebP data URLs in packs/sanguo/illustrations/<bucket>.json, with
illustrations/index.json in the format of the atlas's data/illustrations.json (the pack's data.illustrations). A
picture shared by more than two events is left off them as too generic.

The pages found are kept in tools/sanguo/wiki_pages.json. Events get `source` / `source_zh` links from it here;
people get theirs from build_people.py.
"""
import base64, html, io, json, re, sys, time, urllib.parse, urllib.request, zlib
from PIL import Image

PACK = "packs/sanguo"
UA = {"User-Agent": "SanguoAtlas/1.0 (https://sanguo.yangjie.org; hobby map of the Romance of the Three Kingdoms)"}
FREE = re.compile(r"public domain|^pd|cc0|cc[- ]by|gfdl|attribution", re.I)
BUCKETS, BOX, MAX_SHARED = 8, (320, 280), 2

# English page titles where the plain name is ambiguous or differs; Chinese ones where the name alone is.
PEOPLE_EN = {
 "lady-sun": "Lady Sun", "lady-mi": "Lady Mi", "yan-yan": "Yan Yan (Three Kingdoms)", "xu-chu": "Xu Chu",
 "cai-yan": "Cai Wenji", "wang-lang": "Wang Lang (Cao Wei)", "emperor-xian": "Emperor Xian of Han",
 "zhang-zhao": "Zhang Zhao (Eastern Wu)", "qiao-sisters": "Two Qiaos", "lu-kang": "Lu Kang (Eastern Wu)",
 "yu-ji": "Yu Ji (Taoist)", "diao-chan": "Diaochan", "wang-yun": "Wang Yun (Han dynasty)",
 "liu-zhang": "Liu Zhang (warlord)", "zhang-lu": "Zhang Lu (Han dynasty)", "zhang-jiao": "Zhang Jue",
 "tao-qian": "Tao Qian (Han dynasty)", "xu-you": "Xu You (Han dynasty)", "wang-jun": "Wang Jun (Jin dynasty)", "chen-lin": "Chen Lin (Han dynasty)",
 "zhang-he": "Zhang He", "chen-gong": "Chen Gong", "lu-xun": "Lu Xun (Three Kingdoms)", "yang-hu": "Yang Hu", "du-yu": "Du Yu",
}
PEOPLE_ZH = {
 "lady-sun": "孙夫人 (刘备)", "lady-mi": "糜夫人", "yan-yan": "严颜", "cai-yan": "蔡琰", "wang-lang": "王朗 (曹魏)",
 "emperor-xian": "汉献帝", "zhang-zhao": "张昭 (东吴)", "qiao-sisters": "二乔", "lu-kang": "陆抗", "yu-ji": "于吉",
 "wang-yun": "王允", "liu-zhang": "刘璋", "zhang-lu": "张鲁", "tao-qian": "陶谦", "xu-you": "许攸 (东汉)",
 "wang-jun": "王濬", "zhang-jiao": "张角", "chen-lin": "陈琳 (东汉)", "xu-you": "许攸",
}
# Events with a page of their own: (English title or None, Chinese title or None).
EVENTS = {
 "ch001-peach-garden": ("Oath of the Peach Garden", "桃园结义"),
 "ch001-yellow-turbans": ("Yellow Turban Rebellion", "黄巾之乱"),
 "ch001-changshe": ("Battle of Changshe", "长社之战"),
 "ch002-he-jin": ("Ten Attendants", "十常侍"),
 "ch003-red-hare": ("Red Hare", "赤兔马"),
 "ch004-dethrones-emperor": ("Liu Bian", "刘辩"),
 "ch004-cao-cao-flees": ("Lü Boshe", "吕伯奢"),
 "ch005-eastern-alliance": ("Campaign against Dong Zhuo", "讨伐董卓之战"),
 "ch005-hua-xiong": ("Hua Xiong", "华雄"),
 "ch005-three-heroes-vs-lu-bu": ("Battle of Hulao Pass", "虎牢关之战"),
 "ch007-jieqiao": ("Battle of Jieqiao", "界桥之战"),
 "ch007-sun-jian-dies": ("Battle of Xiangyang (191)", "襄阳之战 (191年)"),
 "ch008-diaochan": ("Diaochan", "连环计"),
 "ch008-phoenix-pavilion": (None, "凤仪亭"),
 "ch009-li-jue-guo-si": ("Li Jue", "李傕"),
 "ch010-xuzhou-massacre": ("Cao Cao's invasion of Xu Province", "曹操攻徐州之战"),
 "ch011-puyang": ("Battle of Yan Province", "兖州之战"),
 "ch015-taishi-ci": ("Taishi Ci", "太史慈"),
 "ch015-sun-ce-east": ("Sun Ce's conquests in Jiangdong", "孙策平定江东"),
 "ch016-halberd-shot": (None, "辕门射戟"),
 "ch016-wancheng": ("Battle of Wancheng", "宛城之战"),
 "ch017-yuan-shu-emperor": ("Yuan Shu", "袁术"),
 "ch019-white-gate-tower": ("Battle of Xiapi", "下邳之战"),
 "ch020-belt-edict": (None, "衣带诏"),
 "ch021-heroes-over-wine": (None, "煮酒论英雄"),
 "ch022-chen-lin": ("Chen Lin (Han dynasty)", "陈琳 (东汉)"),
 "ch025-yan-liang": ("Battle of Boma", "白马之战"),
 "ch026-wen-chou": ("Battle of Yan Ford", "延津之战"),
 "ch027-five-passes": (None, "过五关斩六将"),
 "ch029-sun-ce-dies": ("Yu Ji (Taoist)", "于吉"),
 "ch030-guandu": ("Battle of Guandu", "官渡之战"),
 "ch032-ye-taken": ("Battle of Ye", "邺城之战"),
 "ch033-white-wolf-mountain": ("Battle of White Wolf Mountain", "白狼山之战"),
 "ch034-tan-stream": (None, "的卢"),
 "ch036-xu-shu-recommends": ("Xu Shu", "徐庶"),
 "ch037-three-visits": (None, "三顾茅庐"),
 "ch038-longzhong-plan": ("Longzhong Plan", "隆中对"),
 "ch039-bowang": ("Battle of Bowang", "博望坡之战"),
 "ch041-zhao-yun-changban": ("Battle of Changban", "长坂坡之战"),
 "ch043-debating-the-scholars": (None, "舌战群儒"),
 "ch045-jiang-gan": ("Jiang Gan", "蒋干"),
 "ch046-borrowing-arrows": (None, "草船借箭"),
 "ch046-huang-gai-beaten": (None, "苦肉计"),
 "ch049-red-cliffs": ("Battle of Red Cliffs", "赤壁之战"),
 "ch050-huarong": (None, "华容道"),
 "ch051-first-anger": ("Battle of Jiangling (208)", "江陵之战 (208年)"),
 "ch054-ganlu-temple": ("Ganlu Temple", "甘露寺 (镇江)"),
 "ch058-cuts-his-beard": ("Battle of Tong Pass (211)", "潼关之战"),
 "ch059-blotted-letter": ("Han Sui", "韩遂"),
 "ch060-zhang-song-map": ("Zhang Song (Han dynasty)", "张松 (东汉)"),
 "ch060-liu-bei-enters-shu": ("Liu Bei's takeover of Yi Province", "刘备入蜀"),
 "ch063-pang-tong-dies": (None, "落凤坡"),
 "ch065-ma-chao-joins": (None, "葭萌关"),
 "ch066-single-sword": (None, "单刀会"),
 "ch067-xiaoyao-ford": ("Battle of Xiaoyao Ford", "逍遥津之战"),
 "ch067-hanzhong-taken": ("Battle of Yangping", "阳平关之战"),
 "ch068-gan-ning-raid": ("Battle of Ruxu (217)", "濡须口之战 (217年)"),
 "ch071-dingjun-mountain": ("Battle of Mount Dingjun", "定军山之战"),
 "ch072-chicken-rib": ("Yang Xiu", "杨修"),
 "ch072-xie-valley-retreat": ("Hanzhong Campaign", "汉中之战"),
 "ch073-guan-yu-north": ("Battle of Fancheng", "樊城之战"),
 "ch074-seven-armies": (None, "水淹七军"),
 "ch075-scraping-the-bone": (None, "刮骨疗毒"),
 "ch075-white-robes": ("Lü Meng's invasion of Jing Province", "吕蒙袭荆州"),
 "ch076-maicheng": (None, "麦城"),
 "ch078-cao-cao-dies": ("Cao Cao Mausoleum", "曹操高陵"),
 "ch079-seven-steps": ("Seven Steps Verse", "七步诗"),
 "ch080-cao-pi-emperor": ("End of the Han dynasty", "汉魏禅让"),
 "ch084-yiling": ("Battle of Xiaoting", "夷陵之战"),
 "ch084-stone-sentinel-maze": ("Stone Sentinel Maze", "八阵图"),
 "ch085-baidi": ("Baidicheng", "白帝城"),
 "ch087-southern-campaign": ("Zhuge Liang's Southern Campaign", "诸葛亮南征"),
 "ch090-seven-captures": ("Meng Huo", "七擒孟获"),
 "ch091-memorial": ("Chu Shi Biao", "出师表"),
 "ch093-wang-lang": ("Wang Lang (Cao Wei)", "王朗 (曹魏)"),
 "ch095-jieting": ("Battle of Jieting", "街亭之战"),
 "ch095-empty-fort": ("Empty Fort Strategy", "空城计"),
 "ch096-ma-su-executed": ("Ma Su", "马谡"),
 "ch098-chencang": ("Siege of Chencang", None),
 "ch099-wudu-yinping": ("Zhuge Liang's Northern Expeditions", "诸葛亮北伐"),
 "ch102-wooden-oxen": ("Wooden ox", "木牛流马"),
 "ch104-wuzhang": ("Battle of Wuzhang Plains", "五丈原之战"),
 "ch105-wei-yan": ("Wei Yan", "魏延"),
 "ch106-liaodong": ("Sima Yi's Liaodong campaign", "司马懿征辽东"),
 "ch107-gaopingling": ("Incident at the Gaoping Tombs", "高平陵之变"),
 "ch108-dongxing": ("Battle of Dongxing", "东兴之战"),
 "ch110-taoxi": ("Jiang Wei's Northern Expeditions", "姜维北伐"),
 "ch111-zhuge-dan": ("Zhuge Dan's Rebellion", "诸葛诞之乱"),
 "ch114-cao-mao": ("Cao Mao", "曹髦"),
 "ch116-zhong-hui": ("Conquest of Shu by Wei", "魏灭蜀之战"),
 "ch117-mianzhu": ("Zhuge Zhan", "诸葛瞻"),
 "ch119-zhong-hui-revolt": ("Zhong Hui's Rebellion", "钟会之乱"),
 "ch119-happy-here": (None, "乐不思蜀"),
 "ch120-wu-falls": ("Conquest of Wu by Jin", "晋灭吴之战"),
}

# Pictures chosen by hand from Wikimedia Commons, where a page's lead image belongs to a neighbouring episode or there
# is a painting of the scene itself (the Long Corridor of the Summer Palace has many).
M = "新刊校正古本大字音释三国志通俗演义_明万历十九年书林周曰校刊本_{}.jpg"
FILES = {
 "e:ch004-cao-cao-flees": "Long_Corridor-孟德献刀.JPG",
 "e:ch005-three-heroes-vs-lu-bu": "3_heros_-_Lv_Bu.jpg",
 "e:ch005-eastern-alliance": "Battle_of_Luoyang_Hulao.png",
 "e:ch046-borrowing-arrows": "Long_Corridor-草船借箭.JPG",
 "e:ch048-cao-cao-poem": "Long_Corridor-曹操赋诗.JPG",
 "e:ch059-xu-chu-ma-chao": "Xu_Chu_and_Ma_Chao.JPG",
 "e:ch065-ma-chao-joins": "Zhangfeifightsmachao.jpg",
 "e:ch096-ma-su-executed": "Kongming_subjects_Ma_Su_to_execution.jpg",
 "e:ch104-wooden-statue": "Living_Zongda_Fleeing.jpg",
 "e:ch106-feigned-illness": "司马懿诈病赚曹爽.png",
 "e:ch084-yiling": "火焚連寨.jpg",
 "e:ch034-tan-stream": "Long_Corridor-liubei.jpg",
 "e:ch095-jieting": "Zhuge_Liang_1st_and_2nd_Northern_Expeditions.png",
 "e:ch104-wuzhang": "Temple_of_Marquis_Wu_(Wuzhang_Plains)_entrance_stone2_2016_September.jpg",
 "p:lu-xun": "LuXun.jpg",
 "p:chen-shou": "A_Fragment_of_Biography_of_Bu_Zhi_History_Books_of_Three_Kingdoms_02_2012-12.JPG",
 # Illustrations of the 1591 Zhou Yuejiao edition of the novel, as the pages of these battles use them.
 "e:ch025-yan-liang": M.format("052"),
 "e:ch026-wen-chou": M.format("053"),
 "e:ch051-first-anger": M.format("107"),
 "e:ch084-stone-sentinel-maze": M.format("170"),
}
# Lead images left off: the scene of another event (given to it above), or nothing to do with this one.
SKIP = {"e:ch033-white-wolf-mountain", "e:ch058-cuts-his-beard", "e:ch080-cao-pi-emperor", "e:ch107-gaopingling",
        "p:tao-qian"}


def api(wiki, **q):
    q.update(format="json", formatversion=2)
    url = f"https://{wiki}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(q)
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60))
        except Exception as e:
            print("retry", e, file=sys.stderr)
            time.sleep(3 * (i + 1))
    return {}


def pages(wiki, titles):
    """title -> (resolved title, lead image file or None), for pages that exist and are not disambiguation pages."""
    res = {}
    titles = sorted(set(titles))
    for i in range(0, len(titles), 50):
        chunk = titles[i:i + 50]
        q = api(wiki, action="query", titles="|".join(chunk), prop="pageimages|pageprops", piprop="name",
                redirects=1, **({"converttitles": 1} if wiki == "zh" else {})).get("query", {})
        # Follow each asked title through normalisation, script conversion and redirects to its page; several
        # titles may land on one page.
        fwd = {x["from"]: x["to"] for k in ("normalized", "converted", "redirects") for x in q.get(k, [])}
        got = {pg["title"]: pg for pg in q.get("pages", [])
               if not pg.get("missing") and "disambiguation" not in pg.get("pageprops", {})}
        for t in chunk:
            end = t
            for _ in range(6):
                if end not in fwd:
                    break
                end = fwd[end]
            if end in got:
                res[t] = (end, got[end].get("pageimage"))
        time.sleep(0.3)
    return res


def free_files(wiki, names):
    """File name -> {thumb, license, artist, url} for files with a free licence."""
    res = {}
    names = sorted(set(names))
    for i in range(0, len(names), 50):
        chunk = names[i:i + 50]
        q = api(wiki, action="query", titles="|".join("File:" + n for n in chunk), prop="imageinfo",
                iiprop="url|extmetadata|mime", iiurlwidth=BOX[0]).get("query", {})
        for pg in q.get("pages", []):
            ii = (pg.get("imageinfo") or [None])[0]
            if not ii:
                continue
            m = {k: v.get("value", "") for k, v in ii.get("extmetadata", {}).items()}
            lic = m.get("LicenseShortName") or m.get("License") or ""
            if m.get("NonFree", "").lower() == "true" or not FREE.search(lic):
                continue
            artist = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.get("Artist", "")))).strip()[:120]
            res[pg["title"].split(":", 1)[1].replace(" ", "_")] = {"thumb": ii.get("thumburl") or ii["url"], "license": lic,
                                                                  "artist": artist, "url": ii.get("descriptionurl")}
        time.sleep(0.3)
    return res


def main():
    people = json.load(open(f"{PACK}/people.json", encoding="utf-8"))["people"]
    want = {f"p:{p['id']}": (PEOPLE_EN.get(p["id"], p["name"]), PEOPLE_ZH.get(p["id"], p["name_zh"])) for p in people}
    want.update({f"e:{k}": v for k, v in EVENTS.items()})
    found = {w: pages(w, [t[i] for t in want.values() if t[i]]) for i, w in enumerate(["en", "zh"])}
    url = lambda w, t: f"https://{w}.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"))
    links, picks = {}, {}
    for key, (en, zh) in want.items():
        pe, pz = found["en"].get(en) if en else None, found["zh"].get(zh) if zh else None
        links[key] = {k: v for k, v in (("en", pe and url("en", pe[0])), ("zh", pz and url("zh", pz[0]))) if v}
        picks[key] = [(w, p) for w, p in (("en", pe), ("zh", pz)) if p and p[1]]
    files = {w: free_files(w, [p[1] for ps in picks.values() for ww, p in ps if ww == w]) for w in ("en", "zh")}
    hand = free_files("en", FILES.values())
    chosen = {}
    for key in set(picks) | set(FILES):
        if key in FILES:
            if hand.get(FILES[key]):
                chosen[key] = (FILES[key], FILES[key].rsplit(".", 1)[0].replace("_", " "), hand[FILES[key]])
            continue
        for w, (title, f) in ([] if key in SKIP else picks[key]):
            info = files[w].get(f.replace(" ", "_"))
            # A page whose lead image is only the name in characters falls through to the other language.
            if info and "Chinese_characters" not in f.replace(" ", "_"):
                chosen[key] = (f.replace(" ", "_"), title, info)
                break
    shared = {}
    for key, (f, *_) in chosen.items():
        if key.startswith("e:"):
            shared[f] = shared.get(f, 0) + 1
    keys, images, buckets = {}, {}, {}
    for key, (f, title, info) in sorted(chosen.items(), key=lambda kv: (not kv[0].startswith("p:"), kv[0])):
        if key.startswith("e:") and shared[f] > MAX_SHARED:
            continue
        iid = format(zlib.crc32(f.encode()), "08x")
        if iid not in images:
            try:
                data = urllib.request.urlopen(urllib.request.Request(info["thumb"], headers=UA), timeout=60).read()
                im = Image.open(io.BytesIO(data))
                im.load()
            except Exception as e:
                print("skip", f, e, file=sys.stderr)
                continue
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                bg = Image.new("RGBA", im.size, "white")
                bg.alpha_composite(im)
                im = bg
            im = im.convert("RGB")
            im.thumbnail(BOX, Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, "WEBP", quality=62, method=6)
            b = int(iid, 16) % BUCKETS
            buckets.setdefault(b, {})[iid] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
            images[iid] = {"b": b, "page": title, "license": info["license"], "artist": info["artist"], "url": info["url"],
                           "w": im.width, "h": im.height}
            time.sleep(0.2)
        keys[key] = iid
    import os
    os.makedirs(f"{PACK}/illustrations", exist_ok=True)
    for f in os.listdir(f"{PACK}/illustrations"):
        os.remove(f"{PACK}/illustrations/{f}")
    for b, d in buckets.items():
        with open(f"{PACK}/illustrations/{b}.json", "w") as fh:
            json.dump(d, fh, separators=(",", ":"))
    with open(f"{PACK}/illustrations/index.json", "w", encoding="utf-8") as fh:
        json.dump({"keys": keys, "images": images}, fh, ensure_ascii=False, separators=(",", ":"))
    with open("tools/sanguo/wiki_pages.json", "w", encoding="utf-8") as fh:
        fh.write(json.dumps(links, ensure_ascii=False, indent=1) + "\n")

    # Events link to their pages.
    events = json.load(open(f"{PACK}/events.json", encoding="utf-8"))
    for ev in events:
        ln = links.get("e:" + ev["id"], {})
        for k, w in (("source", "en"), ("source_zh", "zh")):
            ev.pop(k, None)
            if ln.get(w):
                ev[k] = ln[w]
    with open(f"{PACK}/events.json", "w", encoding="utf-8") as fh:
        fh.write(json.dumps(events, ensure_ascii=False, indent=1) + "\n")

    size = sum(os.path.getsize(f"{PACK}/illustrations/{f}") for f in os.listdir(f"{PACK}/illustrations"))
    np, ne = sum(k.startswith("p:") for k in keys), sum(k.startswith("e:") for k in keys)
    print(f"pictures: {np} of {len(people)} people, {ne} of {len(EVENTS)} events, {len(images)} images, {size / 1e6:.1f} MB")
    print(f"links: {sum(1 for k, v in links.items() if v and k.startswith('p:'))} people, "
          f"{sum(1 for k, v in links.items() if v and k.startswith('e:'))} events")
    for key in sorted(want):
        if not links[key]:
            print("  no page:", key, want[key])
    for key in sorted(want):
        if links[key] and key not in keys:
            print("  no free picture:", key, " ".join(links[key].values()))


if __name__ == "__main__":
    main()
