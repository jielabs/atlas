#!/bin/sh
# Check, build and publish the stand-alone Three Kingdoms site.
#
# Usage: tools/sanguo/deploy.sh [user@host | /local/dir]
#   from a workstation:        tools/sanguo/deploy.sh               (copies to jie@dev:/var/www/sanguo)
#   on the server itself:      tools/sanguo/deploy.sh /var/www/sanguo
#
# The server side was set up once: /var/www/sanguo owned by the deploy user, the nginx site in
# tools/sanguo/nginx/ installed in sites-available and enabled, and a certificate from `certbot --nginx`.
# After that a deploy is only this: unchanged files are not sent again, deleted ones are removed.
set -e
cd "$(dirname "$0")/../.."
TARGET="${1:-jie@dev}"
python3 tools/packs/check_pack.py packs/sanguo >/dev/null
python3 tools/sanguo/build_site.py --tiles full --out dist/sanguo
case "$TARGET" in
  /*) rsync -a --delete dist/sanguo/ "$TARGET/" ;;
  *)  rsync -az --delete dist/sanguo/ "$TARGET:/var/www/sanguo/" ;;
esac
echo "published: https://sanguo.192-155-81-57.sslip.io/"
