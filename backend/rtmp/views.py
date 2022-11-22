from django.http import JsonResponse
from .tasks import push_stream
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def start(request):
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8')) 
        ffmpeg_command = body["ffmpegCommand"]
        ip_addr = request.META.get('REMOTE_ADDR')
        push_stream.delay(ip_addr, ffmpeg_command)
        data = {
            "ip": ip_addr
        }
        return JsonResponse(data)