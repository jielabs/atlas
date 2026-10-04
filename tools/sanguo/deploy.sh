#!/bin/sh
# Check, build and publish the stand-alone Three Kingdoms site.
#
# Usage: tools/sanguo/deploy.sh [user@host | /local/dir]
#   from a workstation:        tools/sanguo/deploy.sh               (copies to jie@dev:/var/www/atlas)
#   on the server itself:      tools/sanguo/deploy.sh /var/www/atlas
#
# The server side was set up once: /var/www/atlas owned by the deploy user, the nginx site in tools/sanguo/nginx/
# installed in sites-available and enabled, and a Let's Encrypt certificate issued through the webroot
# /var/www/acme (atlas.yangjie.org is proxied by Cloudflare, which fetches from the server over HTTPS).
# After that a deploy is only this: unchanged files are not sent again, deleted ones are removed.
set -e
cd "$(dirname "$0")/../.."
TARGET="${1:-jie@dev}"
python3 tools/packs/check_pack.py packs/sanguo >/dev/null || { python3 tools/packs/check_pack.py packs/sanguo | grep -E "ERROR|errors"; exit 1; }
python3 tools/sanguo/build_site.py --tiles full --out dist/atlas
case "$TARGET" in
  /*) rsync -a --delete dist/atlas/ "$TARGET/" ;;
  *)  rsync -az --delete dist/atlas/ "$TARGET:/var/www/atlas/" ;;
esac
echo "published: https://atlas.yangjie.org/"
