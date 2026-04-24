from urllib.parse import parse_qs

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.streaming import end_stream_session, get_active_stream_session, validate_publish_attempt


def _get_callback_value(request, key):
    value = request.data.get(key) or request.query_params.get(key)
    if value:
        return value

    raw_args = request.data.get('args') or request.query_params.get('args')
    if not raw_args:
        return None

    return parse_qs(raw_args).get(key, [None])[0]


class InternalPublishAuthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        playback_id = _get_callback_value(request, 'name') or _get_callback_value(request, 'playback_id')
        stream_key = _get_callback_value(request, 'stream_key')

        if validate_publish_attempt(playback_id=playback_id, plaintext_key=stream_key) is None:
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


class InternalPublishEndView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        playback_id = _get_callback_value(request, 'name') or _get_callback_value(request, 'playback_id')
        stream_session = get_active_stream_session(playback_id=playback_id)
        if stream_session is not None:
            end_stream_session(stream_session=stream_session)

        return Response(status=status.HTTP_204_NO_CONTENT)