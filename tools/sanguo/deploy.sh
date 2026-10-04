#!/bin/sh
# Check, build and publish the stand-alone Three Kingdoms site.
#
# Usage: tools/sanguo/deploy.sh [user@host]        (default: jie@dev)
#
# The server side was set up once: /var/www/sanguo owned by the deploy user, the nginx site in
# tools/sanguo/nginx/ installed in sites-available and enabled, and a certificate from `certbot --nginx`.
# After that a deploy is only this: unchanged files are not sent again, deleted ones are removed.
set -e
cd "$(dirname "$0")/../.."
TARGET="${1:-jie@dev}"
python3 tools/packs/check_pack.py packs/sanguo >/dev/null
python3 tools/sanguo/build_site.py --tiles full --out dist/sanguo
rsync -az --delete dist/sanguo/ "$TARGET:/var/www/sanguo/"
echo "published: https://sanguo.192-155-81-57.sslip.io/"
