"""Check a data pack against what app.js expects, and report coverage.

Usage: python3 tools/packs/check_pack.py <pack dir>        (e.g. packs/xiyouji, packs/sanguo)

Errors fail the run (exit 1); warnings only print. The engine silently ignores malformed data, so this is the
only way to know a pack is sound before opening it. Rules every pack shares come first; RULES below adds what a
particular pack promises about itself (its footing field, its chapters, its historical notes).
"""
import json, os, re, sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
PACK = sys.argv[1].rstrip("/")
# The nine categories hardcoded in app.js (CATS).
CATS = {"war", "politics", "reform", "rebellion", "diplomacy", "economy", "culture", "science", "society"}
# Per pack, by manifest id. `field`: a required event field and its allowed values. `chapters`: (first, last, the
# event field holding the chapter); every chapter should have an event. `notes`: values of `field` whose events must
# carry a 史实 / Historically clause (None: none required, but zh and en must agree). `routes`: a GeoJSON file of
# movements (loaded by a plugin) whose feature ids tour steps may name in "route".
RULES = {
 "xiyouji": {"field": ("ground", {"real", "identified", "projected", "invented"}), "chapters": (1, 100, "year"), "notes": None},
 "sanguo": {"field": ("truth", {"history", "embellished", "fiction"}), "chapters": (1, 120, "chapter"),
            "notes": {"embellished", "fiction"}, "routes": "layers/campaigns.geojson"},
}
GEOM_OK = {"fill": {"Polygon", "MultiPolygon"}, "line": {"LineString", "MultiLineString", "Polygon", "MultiPolygon"},
           "circle": {"Point", "MultiPoint"}}

errors, warnings = [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)
def load(rel):
    p = os.path.join(PACK, rel)
    if not os.path.exists(p):
        err(f"missing file: {p}")
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{rel}: invalid JSON, {e}")
        return None

def pair(o, key, where):
    """Text fields come in pairs: x (English) and x_zh."""
    for k in (key, key + "_zh"):
        if not str(o.get(k, "")).strip():
            err(f"{where}: {k} is empty")

def inbox(lon, lat, where):
    w, e, s, n = BOX
    if not (isinstance(lon, (int, float)) and isinstance(lat, (int, float))):
        err(f"{where}: lon/lat must be numbers, got {lon!r},{lat!r}")
    elif not (w <= lon <= e and s <= lat <= n):
        err(f"{where}: {lon},{lat} is outside the pack's box {BOX}")

# ---- manifest -------------------------------------------------------------
m = load("manifest.json") or {}
RULE = RULES.get(m.get("id"), {})
# Coordinates must lie near the pack's region (3 degrees of slack); anything further is a typo.
_poly = (m.get("region") or {}).get("polygon") or [[-180, -85], [180, 85]]
BOX = (min(p[0] for p in _poly) - 3, max(p[0] for p in _poly) + 3, min(p[1] for p in _poly) - 3, max(p[1] for p in _poly) + 3)
if m.get("atlas") != 1: err("manifest: atlas must be 1")
if not re.fullmatch(r"[a-z0-9-]+", str(m.get("id", ""))): err("manifest: id must match [a-z0-9-]+")
rng = m.get("range") or {}
START, END = rng.get("start"), rng.get("end")
if not isinstance(START, int) or not isinstance(END, int) or START >= END:
    err("manifest: range needs integer start < end")
    START, END = 1, 100
for k in ("eras", "events"):
    if not (m.get("data") or {}).get(k): err(f"manifest: data.{k} is required")
for L in m.get("layers", []):
    if not re.fullmatch(r"[a-z0-9-]+", str(L.get("id", ""))): err(f"manifest layer {L.get('id')!r}: bad id")
    if L.get("type") not in (None, "fill", "line", "circle"): err(f"layer {L['id']}: type must be fill/line/circle")
    pair(L, "name", f"layer {L.get('id')}")
for p in m.get("plugins", []):
    if not os.path.exists(os.path.join(PACK, p)): err(f"manifest: plugin {p} does not exist")
if m.get("library"):
    lib_path = os.path.normpath(os.path.join(PACK, m["library"]))
    lib = json.load(open(lib_path, encoding="utf-8")) if os.path.exists(lib_path) else None
    if lib is None: err(f"manifest: library {m['library']} does not exist")
    else:
        for e in lib.get("packs", []):
            if e.get("manifest") and not os.path.exists(os.path.join(os.path.dirname(lib_path), e["manifest"])):
                err(f"library: {e.get('id')} points at missing {e['manifest']}")
        if m.get("id") not in {e.get("id") for e in lib.get("packs", [])}:
            err(f"library: no entry for this pack's id {m.get('id')!r}")
if (m.get("refs") or {}).get("url", "").startswith("TODO"):
    warn("manifest: refs.url is still a placeholder; chapter links will be broken")

# ---- eras -----------------------------------------------------------------
eras = (load("eras.json") or {}).get("eras") or []
if not eras: err("eras.json: no eras")
seen = set()
for i, e in enumerate(eras):
    where = f"era {e.get('id', i)}"
    if not re.fullmatch(r"[a-z0-9-]+", str(e.get("id", ""))): err(f"{where}: bad id")
    if e["id"] in seen: err(f"{where}: duplicate id")
    seen.add(e.get("id"))
    pair(e, "name", where); pair(e, "summary", where)
    if not 1 <= len(str(e.get("glyph", ""))) <= 2: err(f"{where}: glyph must be 1-2 characters")
    for k in ("short", "tiny"):
        if not str(e.get(k, "")).strip(): warn(f"{where}: {k} missing, the timeline falls back to the full name")
    if not isinstance(e.get("start"), int) or not isinstance(e.get("end"), int): err(f"{where}: start/end must be integers")
    snaps = e.get("snapshots") or []
    for j, sn in enumerate(snaps):
        f = os.path.normpath(os.path.join(PACK, str(sn.get("borders", "")).split("#")[0]))
        if not os.path.exists(f): err(f"{where} snapshot {j + 1}: {sn.get('borders')} does not exist")
        if not isinstance(sn.get("from"), int): err(f"{where} snapshot {j + 1}: from must be an integer")
    if snaps and snaps[0].get("from") != e.get("start"):
        err(f"{where}: the first snapshot must start at the era's start {e.get('start')}")
if eras and all(isinstance(e.get("start"), int) and isinstance(e.get("end"), int) for e in eras):
    if eras[0]["start"] != START or eras[-1]["end"] != END:
        err(f"eras must span the manifest range {START}-{END}, got {eras[0]['start']}-{eras[-1]['end']}")
    for a, b in zip(eras, eras[1:]):
        if b["start"] != a["end"] + 1:
            err(f"eras must be back to back with no gaps: {a['id']} ends {a['end']}, {b['id']} starts {b['start']}")

def era_of(y):
    return next((e for e in eras if e.get("start", 0) <= y <= e.get("end", 0)), None)

# ---- events ---------------------------------------------------------------
events = load("events.json") or []
if not isinstance(events, list): err("events.json: must be a list"); events = []
ids, per_era, grounds = set(), {}, {}
for i, ev in enumerate(events):
    where = f"event {ev.get('id', i)}"
    if not str(ev.get("id", "")).strip(): err(f"{where}: id is required")
    elif ev["id"] in ids: err(f"{where}: duplicate id")
    ids.add(ev.get("id"))
    pair(ev, "title", where); pair(ev, "place", where); pair(ev, "summary", where)
    y = ev.get("year")
    if not isinstance(y, int): err(f"{where}: year (the chapter number) must be an integer")
    elif not START <= y <= END: err(f"{where}: year {y} is outside {START}-{END}")
    else:
        e = era_of(y)
        if not e: err(f"{where}: chapter {y} falls in no era")
        else: per_era[e["id"]] = per_era.get(e["id"], 0) + 1
    if ev.get("level") not in (1, 2, 3): err(f"{where}: level must be 1, 2 or 3")
    if ev.get("category") not in CATS: err(f"{where}: category {ev.get('category')!r} is not one of {sorted(CATS)}")
    inbox(ev.get("lon"), ev.get("lat"), where)
    zh_note, en_note = "史实：" in str(ev.get("summary_zh", "")), "Historically:" in str(ev.get("summary", ""))
    if zh_note != en_note: err(f"{where}: the 史实 note and the Historically note must come together")
    if RULE.get("field"):
        key, allowed = RULE["field"]
        g = ev.get(key)
        if g not in allowed: err(f"{where}: {key} {g!r} must be one of {sorted(allowed)}")
        else:
            grounds[g] = grounds.get(g, 0) + 1
            if RULE.get("notes") and g in RULE["notes"] and not zh_note:
                err(f"{where}: {key} is {g}, so the summary must say what really happened (史实： / Historically:)")
    if RULE.get("chapters"):
        c0, c1, ck = RULE["chapters"]
        c = ev.get(ck)
        if not isinstance(c, int) or not c0 <= c <= c1: err(f"{where}: {ck} must be a chapter {c0}-{c1}")

# ---- routes (movements a plugin draws, named by tour steps) ---------------------
route_ids = set()
if RULE.get("routes"):
    rg = load(RULE["routes"]) or {}
    for j, f in enumerate(rg.get("features", [])):
        pr, gt = f.get("properties", {}), (f.get("geometry") or {}).get("type")
        fw = f"{RULE['routes']}#{pr.get('id', j)}"
        if not pr.get("id"): err(f"{fw}: id is required")
        elif pr["id"] in route_ids: err(f"{fw}: duplicate id")
        route_ids.add(pr.get("id"))
        if gt not in ("LineString", "MultiLineString"): err(f"{fw}: must be a LineString or MultiLineString, not {gt}")
        if not (isinstance(pr.get("from"), int) and isinstance(pr.get("to"), int) and pr["from"] < pr["to"]):
            err(f"{fw}: needs integer from < to")
        elif not (START <= pr["from"] <= END): err(f"{fw}: from {pr['from']} is outside {START}-{END}")
        if not pr.get("color"): err(f"{fw}: color is required")
        pair(pr, "name", fw)
        for line in (f["geometry"]["coordinates"] if gt == "MultiLineString" else [f.get("geometry", {}).get("coordinates", [])]):
            for x, y in line: inbox(x, y, fw)

# ---- tours ----------------------------------------------------------------
tours = load("tours.json") or []
if not isinstance(tours, list): err("tours.json: must be a list"); tours = []
tids = set()
for i, t in enumerate(tours):
    where = f"tour {t.get('id', i)}"
    if not str(t.get("id", "")).strip(): err(f"{where}: id is required")
    elif t["id"] in tids: err(f"{where}: duplicate id")
    tids.add(t.get("id"))
    pair(t, "title", where)
    if t.get("era") not in seen: err(f"{where}: era {t.get('era')!r} is not one of the pack's eras")
    steps = t.get("steps") or []
    if not steps: err(f"{where}: no steps")
    for j, s in enumerate(steps):
        sw = f"{where} step {j + 1}"
        if not isinstance(s.get("year"), int) or not START <= s["year"] <= END: err(f"{sw}: year must be {START}-{END}")
        at = s.get("at")
        if not (isinstance(at, list) and len(at) == 2): err(f"{sw}: at must be [lon, lat]")
        else: inbox(at[0], at[1], sw)
        pair(s, "text", sw)
        if s.get("event") and s["event"] not in ids: err(f"{sw}: event {s['event']!r} is not in events.json")
        for r in ([s["route"]] if isinstance(s.get("route"), str) else s.get("route") or []):
            if r not in route_ids: err(f"{sw}: route {r!r} is not in {RULE.get('routes') or 'any routes file'}")

# ---- layers ---------------------------------------------------------------
for L in m.get("layers", []):
    gj = load(L["data"]) if isinstance(L.get("data"), str) else None
    if gj is None: continue
    if gj.get("type") != "FeatureCollection": err(f"{L['data']}: not a FeatureCollection"); continue
    feats = gj.get("features") or []
    if not feats: warn(f"{L['data']}: no features yet")
    ok = GEOM_OK.get(L.get("type"))
    for j, f in enumerate(feats):
        fw = f"{L['data']}#{j}"
        gt = (f.get("geometry") or {}).get("type")
        if ok and gt not in ok: err(f"{fw}: {gt} will not draw in a {L['type']} layer")
        props = f.get("properties") or {}
        for k in ("from", "to"):
            if k in props and not isinstance(props[k], int): err(f"{fw}: {k} must be an integer chapter")
        if "from" in props and "to" in props and props["from"] >= props["to"]:
            err(f"{fw}: from {props['from']} must be below to {props['to']} (the range is [from, to))")
        if not (props.get("name") or props.get("text")): warn(f"{fw}: no name or text, so it opens no card")

# ---- report ---------------------------------------------------------------
print(f"{PACK}: {len(eras)} eras, {len(events)} events, {len(tours)} tours")
if eras:
    print("\nevents per era")
    for e in eras:
        n = per_era.get(e["id"], 0)
        span = e["end"] - e["start"] + 1
        flag = "  <- empty" if n == 0 else ""
        unit = "ch" if RULE.get("chapters", (0, 0, ""))[2] == "year" else "yr"
        chs = f"  ch {e['chapters'][0]}-{e['chapters'][1]}" if e.get("chapters") else ""
        print(f"  {e['id']:<14} {unit} {e['start']:>3}-{e['end']:<3} ({span:>2} {unit}){chs:<14}  {n:>3} events{flag}")
if grounds:
    print(f"\nevents by {RULE['field'][0]}: " + ", ".join(f"{k} {v}" for k, v in sorted(grounds.items())))
if events:
    notes = sum("史实：" in str(ev.get("summary_zh", "")) for ev in events)
    print(f"historical notes: {notes} of {len(events)} ({notes / len(events):.0%})")
if events and RULE.get("chapters"):
    c0, c1, ck = RULE["chapters"]
    have = {ev.get(ck) for ev in events}
    gaps = [c for c in range(c0, c1 + 1) if c not in have]
    print(f"chapters with no event: {len(gaps)}" + (f" -> {gaps}" if 0 < len(gaps) <= 40 else ""))

for w in warnings: print(f"WARN  {w}")
for e in errors: print(f"ERROR {e}")
print(f"\n{len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
