#!/bin/sh
# Publish the development site, https://atlas.yangjie.org/ (nginx on the VPS `dev`, behind Cloudflare).
#
# Usage: tools/sanguo/deploy_dev.sh [user@host | /local/dir]
#   from a workstation:   tools/sanguo/deploy_dev.sh                  (copies to jie@dev:/var/www/atlas)
#   on the server itself: tools/sanguo/deploy_dev.sh /var/www/atlas
#
# Any state of the working tree may go to dev: version.json records the commit and whether it had uncommitted
# changes, and the site is marked " · dev" and kept out of search engines. Once it looks right there, promote the
# same commit with tools/sanguo/deploy_prod.sh.
#
# The server side was set up once: /var/www/atlas owned by the deploy user, the nginx site in tools/sanguo/nginx/
# installed in sites-available and enabled, and a Let's Encrypt certificate issued through the webroot
# /var/www/acme (atlas.yangjie.org is proxied by Cloudflare, which fetches from the server over HTTPS).
set -e
cd "$(dirname "$0")/../.."
TARGET="${1:-jie@dev}"
python3 tools/packs/check_pack.py packs/sanguo >/dev/null || { python3 tools/packs/check_pack.py packs/sanguo | grep -E "ERROR|errors"; exit 1; }
python3 tools/sanguo/build_site.py --tiles full --out dist/atlas-dev --env dev
case "$TARGET" in
  /*) rsync -a --delete dist/atlas-dev/ "$TARGET/" ;;
  *)  rsync -az --delete dist/atlas-dev/ "$TARGET:/var/www/atlas/" ;;
esac
echo "published to dev: https://atlas.yangjie.org/  $(cat dist/atlas-dev/version.json)"
