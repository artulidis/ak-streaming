import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from .models import AccountStreamKey, StreamSession


class LiveSessionConflict(Exception):
    pass


def _generate_secret(length=32):
    return secrets.token_urlsafe(length)


def generate_playback_id():
    return _generate_secret(18)


def generate_stream_key():
    return _generate_secret(24)


@transaction.atomic
def rotate_account_stream_key(*, user):
    plaintext = generate_stream_key()
    stream_key, _ = AccountStreamKey.objects.update_or_create(
        user=user,
        defaults={
            'stream_key_hash': make_password(plaintext),
            'stream_key_last4': plaintext[-4:],
            'rotated_at': timezone.now(),
        },
    )
    return stream_key, plaintext


def verify_account_stream_key(*, user, plaintext_key):
    if not plaintext_key:
        return False

    account_stream_key = AccountStreamKey.objects.filter(user=user).first()
    if account_stream_key is None:
        return False

    return check_password(plaintext_key, account_stream_key.stream_key_hash)


def get_active_stream_session(*, video_id=None, playback_id=None):
    queryset = StreamSession.objects.select_related('user', 'video').filter(is_live=True)

    if video_id is not None:
        queryset = queryset.filter(video_id=video_id)

    if playback_id is not None:
        queryset = queryset.filter(playback_id=playback_id)

    return queryset.first()


@transaction.atomic
def create_stream_session(*, user, video):
    if StreamSession.objects.filter(video=video, is_live=True).exists():
        raise LiveSessionConflict('This video already has an active live session.')

    if StreamSession.objects.filter(user=user, is_live=True).exists():
        raise LiveSessionConflict('This user already has an active live session.')

    return StreamSession.objects.create(
        user=user,
        video=video,
        playback_id=generate_playback_id(),
    )


@transaction.atomic
def end_stream_session(*, stream_session):
    if not stream_session.is_live:
        return stream_session

    stream_session.is_live = False
    stream_session.ended_at = timezone.now()
    stream_session.save(update_fields=['is_live', 'ended_at'])
    return stream_session


def validate_publish_attempt(*, playback_id, plaintext_key):
    stream_session = get_active_stream_session(playback_id=playback_id)
    if stream_session is None:
        return None

    if not verify_account_stream_key(user=stream_session.user, plaintext_key=plaintext_key):
        return None

    return stream_session