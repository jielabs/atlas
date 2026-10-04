#!/bin/sh
# Check, build and publish the stand-alone Three Kingdoms site on Cloudflare, at https://sanguo.yangjie.org/.
#
# Usage: tools/sanguo/deploy_cloudflare.sh        (needs `npx wrangler login` once)
#
# The site runs as Cloudflare Workers static assets (tools/sanguo/wrangler.jsonc): no Worker code and no server;
# Cloudflare serves the files from its edge and keeps the DNS record and certificate for the custom domain.
# The same build can also be served by nginx (tools/sanguo/deploy.sh, atlas.yangjie.org).
set -e
cd "$(dirname "$0")/../.."
python3 tools/packs/check_pack.py packs/sanguo >/dev/null || { python3 tools/packs/check_pack.py packs/sanguo | grep -E "ERROR|errors"; exit 1; }
python3 tools/sanguo/build_site.py --tiles full --out dist/atlas --pages
npx --yes wrangler deploy --config tools/sanguo/wrangler.jsonc
echo "published: https://sanguo.yangjie.org/"
