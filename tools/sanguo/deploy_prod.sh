#!/bin/sh
# Promote to production, https://sanguo.yangjie.org/ (Cloudflare Workers static assets: no server, no Worker code;
# Cloudflare keeps the custom domain's DNS record and certificate).
#
# Usage: tools/sanguo/deploy_prod.sh [--force]        (needs `npx wrangler login` once)
#
# Production only takes what development has shown: the working tree must be clean, the commit must be on GitHub,
# and https://atlas.yangjie.org/ must be running that same commit (publish it there first with deploy_dev.sh).
# --force skips the last check, for an urgent fix.
set -e
cd "$(dirname "$0")/../.."
fail() { echo "deploy_prod: $*" >&2; exit 1; }
FORCE=; [ "$1" = "--force" ] && FORCE=1

[ -z "$(git status --porcelain --untracked-files=no)" ] || fail "uncommitted changes; commit, publish to dev, then promote"
COMMIT=$(git rev-parse --short HEAD)
git fetch -q origin || fail "could not reach GitHub to check that $COMMIT is pushed"
[ -n "$(git branch -r --contains HEAD)" ] || fail "commit $COMMIT is not on GitHub yet; push it first"
DEV=$(curl -fsS --max-time 15 https://atlas.yangjie.org/version.json \
      | python3 -c 'import json, sys; d = json.load(sys.stdin); print(d["commit"] + ("+changes" if d["dirty"] else ""))') || DEV=unreachable
if [ "$DEV" != "$COMMIT" ]; then
  [ -n "$FORCE" ] || fail "dev runs $DEV, not $COMMIT; publish it with deploy_dev.sh and check it there first (or --force)"
  echo "deploy_prod: dev runs $DEV, promoting $COMMIT anyway (--force)" >&2
fi

python3 tools/packs/check_pack.py packs/sanguo >/dev/null || { python3 tools/packs/check_pack.py packs/sanguo | grep -E "ERROR|errors"; exit 1; }
python3 tools/sanguo/build_site.py --tiles full --out dist/atlas-prod --env prod --pages
npx --yes wrangler deploy --config tools/sanguo/wrangler.jsonc
echo "published to prod: https://sanguo.yangjie.org/  $(cat dist/atlas-prod/version.json)"
