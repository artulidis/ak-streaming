FROM tiangolo/nginx-rtmp

COPY stream/ /var/www/stream/
COPY nginx.conf /etc/nginx/nginx.conf
COPY http.conf /etc/nginx/conf.d/http.conf
COPY rtmp.conf /etc/nginx/conf.d/rtmp.conf

RUN apt-get update && apt-get install -y ffmpeg
RUN chgrp www-data /var/www/stream/rec/ && chmod g+rwxs /var/www/stream/rec/