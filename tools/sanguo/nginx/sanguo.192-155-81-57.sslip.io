# sanguo — Romance of the Three Kingdoms on the atlas engine. A static site in /var/www/sanguo, built by
# tools/sanguo/build_site.py in the atlas repo (branch sanguo) and copied with rsync. TLS block is added by certbot.
# To remove: delete this file and its link in sites-enabled, reload nginx, and delete /var/www/sanguo.
server {
    server_name sanguo.192-155-81-57.sslip.io;
    listen 80;
    listen [::]:80;

    root /var/www/sanguo;
    index index.html;
    autoindex off;

    gzip on;
    gzip_types text/css application/javascript application/json application/geo+json image/svg+xml;
    gzip_min_length 1024;

    # .geojson is not in mime.types; give it its type so it is gzipped too.
    location ~* \.geojson$ {
        default_type application/geo+json;
        add_header Cache-Control "no-cache";
    }
    # Page, code and data revalidate on every load (the engine fetches data with cache: no-cache anyway), so a
    # new deploy shows at once; unchanged files come back as 304.
    location ~* \.(html|js|css|json)$ {
        add_header Cache-Control "no-cache";
    }
    # Elevation and imagery archives: large, and rebuilt rarely.
    location /tiles/ {
        add_header Cache-Control "public, max-age=2592000";
    }
    location / {
        try_files $uri $uri/ =404;
    }
}
