"""Build a stand-alone static site that shows only the Three Kingdoms pack.

Usage: python3 tools/sanguo/build_site.py [--tiles full|lean] [--out dist/atlas] [--pages] [--env prod|dev]

The engine needs only a small part of the atlas to run one pack shown alone: the page, the world maps around the
pack's East Asia window for its years, the river and landscape names, and the elevation and imagery tiles. This
copies exactly that, plus the pack, into one folder that any static web server can serve.

Tiles: `full` keeps every bundled zoom that touches the pack's area (the page works with no outside tile source);
`lean` keeps zooms 0-5 only, and past them the browser fetches AWS Terrain Tiles and EOX Sentinel-2 itself, as
app.js already does when it can reach them (LIVE).

The root address opens the pack: index.html names it in <html data-pack data-packonly>, so the address stays
clean. The manifest's library is dropped, since the site has one book.

--pages adds a _headers file for Cloudflare (Workers static assets or Pages), which does there what the nginx site
in tools/sanguo/nginx/ does: tile archives cached for 30 days, .geojson given its type. Cloudflare already
revalidates everything else on each load.

Every build writes version.json (commit, branch, whether the working tree had uncommitted changes, build time), so
each environment says what it runs; tools/sanguo/deploy_prod.sh compares it before promoting. --env dev marks the
build as the development site: " · dev" after the pack's name (tab title and panels) and a robots.txt that keeps
search engines out.
"""
import argparse, datetime, gzip, json, math, os, re, shutil, subprocess

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
PACK = "packs/sanguo"
# Tiles: everything the pack's region can show, with a margin for panning.
BBOX = (88.0, 14.0, 132.0, 47.0)  # west, south, east, north
LEAN_MAX_ZOOM = 5

ap = argparse.ArgumentParser()
ap.add_argument("--tiles", choices=["full", "lean"], default="full")
ap.add_argument("--out", default="dist/atlas")
ap.add_argument("--pages", action="store_true", help="add a _headers file for Cloudflare")
ap.add_argument("--env", choices=["prod", "dev"], default="prod", help="dev marks the site as the development one")
args = ap.parse_args()
OUT = os.path.join(ROOT, args.out)


def src(p): return os.path.join(ROOT, p)
def dst(p): return os.path.join(OUT, p)


def copy(p, to=None):
    os.makedirs(os.path.dirname(dst(to or p)), exist_ok=True)
    shutil.copy2(src(p), dst(to or p))


def write(p, text):
    os.makedirs(os.path.dirname(dst(p)), exist_ok=True)
    open(dst(p), "w", encoding="utf-8").write(text)


if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)

# The page and its assets.
for p in ["app.js", "style.css", "vendor/maplibre-gl.css", "LICENSE",
          "docs/img/favicon.svg", "docs/img/icon-32.png", "docs/img/icon-180.png"]:
    copy(p)
manifest = json.load(open(src(f"{PACK}/manifest.json"), encoding="utf-8"))
html = open(src("index.html"), encoding="utf-8").read()
title = f"{manifest['name_zh']} · {manifest['name']}" + (" (dev)" if args.env == "dev" else "")
html = html.replace("<title>Atlas</title>", f"<title>{title}</title>")
assert html.count('<html lang="zh-CN">') == 1
html = html.replace('<html lang="zh-CN">', f'<html lang="zh-CN" data-pack="{PACK}/manifest.json" data-packonly="1">')
write("index.html", html)

# Data the engine always reads (app.js init and buildStyle), and the illustration index it reads when a story opens;
# the pack's events have no pictures, so an empty index stands in for the atlas's.
for p in ["data/regions.json", "data/world/index.json", "data/geo/rivers.geojson", "data/geo/lakes.geojson",
          "data/geo/old-rivers.geojson", "data/geo/features.json"]:
    copy(p)
write("data/illustrations.json", json.dumps({"keys": {}, "images": {}}))

# The pack, without the shelf and without its working notes.
eras = json.load(open(src(f"{PACK}/eras.json"), encoding="utf-8"))
for dirpath, _, files in os.walk(src(PACK)):
    for f in files:
        rel = os.path.relpath(os.path.join(dirpath, f), ROOT)
        if not f.endswith(".md"):
            copy(rel)
manifest.pop("library", None)
if args.env == "dev":
    manifest["name"] += " · dev"
    manifest["name_zh"] += " · dev"
write(f"{PACK}/manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

# Border maps the pack's periods name outside the pack (the atlas's Eastern Han map), and the outer world maps
# drawn around the East Asia window in the pack's years.
for e in eras["eras"]:
    for s in e.get("snapshots", []):
        p = os.path.normpath(os.path.join(PACK, s["borders"].split("#")[0]))
        if not p.startswith(PACK):
            copy(p)
world = json.load(open(src("data/world/index.json"), encoding="utf-8"))
start, end = manifest["range"]["start"], manifest["range"]["end"]
for i, w in enumerate(world):
    nxt = world[i + 1]["from"] if i + 1 < len(world) else 10**6
    if w["from"] <= end and nxt - 1 >= start:
        for k in ("outer", "full"):
            if w.get(k):
                copy(w[k])


# Tiles. Archives are named <z>-<x block>-<y block>.png: one per zoom at z <= 3, 8x8 tiles at z 4-8, 16x16 at z9
# (tools/pack_tiles.py). Keep those whose tile block touches the box.
def tile_xy(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def keep(name):
    z, bx, by = map(int, name[:-4].split("-"))
    if z <= 3:
        return True
    if args.tiles == "lean" and z > LEAN_MAX_ZOOM:
        return False
    sh = 4 if z >= 9 else 3
    x0, y0 = tile_xy(BBOX[0], BBOX[3], z)
    x1, y1 = tile_xy(BBOX[2], BBOX[1], z)
    return (x0 >> sh) <= bx <= (x1 >> sh) and (y0 >> sh) <= by <= (y1 >> sh)


kept = dropped = 0
for d in ["tiles/pack", "tiles/sat"]:
    for f in sorted(os.listdir(src(d))):
        if re.fullmatch(r"\d+-\d+-\d+\.png", f) and keep(f):
            copy(f"{d}/{f}"); kept += 1
        else:
            dropped += 1


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


version = {"commit": git("rev-parse", "--short", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
           "dirty": bool(git("status", "--porcelain", "--untracked-files=no")), "env": args.env,
           "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
write("version.json", json.dumps(version) + "\n")
if args.env == "dev":
    write("robots.txt", "User-agent: *\nDisallow: /\n")

if args.pages:
    write("_headers", "/tiles/*\n  Cache-Control: public, max-age=2592000\n"
                      "/*.geojson\n  Content-Type: application/geo+json\n")

# Report.
def size(path):
    return sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(path) for f in fs)


def gz(path):
    return sum(len(gzip.compress(open(os.path.join(dp, f), "rb").read(), 6))
               for dp, _, fs in os.walk(path) for f in fs if f.endswith((".js", ".css", ".html", ".json", ".geojson", ".svg")))


mb = lambda b: f"{b / 2**20:.1f} MB"
total = size(OUT)
print(f"{args.out} ({args.tiles} tiles): {mb(total)}, {sum(len(fs) for _, _, fs in os.walk(OUT))} files; "
      f"tile archives kept {kept}, dropped {dropped}")
for part in ["tiles/pack", "tiles/sat", "data", PACK, "."]:
    p = dst(part)
    if part == ".":
        rest = total - sum(size(dst(x)) for x in ["tiles", "data", "packs"])
        print(f"  {'page (html, js, css, icons)':<28} {mb(rest)}")
    else:
        print(f"  {part:<28} {mb(size(p))}")
print(f"  text files gzipped: {mb(gz(OUT))} (served compressed by any web server with gzip on)")
