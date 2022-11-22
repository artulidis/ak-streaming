from __future__ import absolute_import, unicode_literals
from celery import Celery, shared_task
import os

# app = Celery('tasks', broker='redis://localhost:6379/0')
app = Celery('tasks', broker='redis://redis:6379/0')

@shared_task()
def push_stream(ip_addr, ffmpeg_command):
    ffmpeg_command = ffmpeg_command.replace("127.0.0.1", ip_addr)
    print(ffmpeg_command)
    os.system(ffmpeg_command)
    # os.system(f"ffmpeg -f video4linux2 -i /dev/video0 -t 5 -vcodec libx264 -preset ultrafast -pix_fmt yuv420p -s 1200x720 -r 30 -b:v 1500k -maxrate 7000k -c:a aac -b:a 128k -ac 2 -ar 44100 -f flv rtmp://127.0.0.1:1935/live/0006")