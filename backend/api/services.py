from django.db import transaction
from django.db.models import Count
from rest_framework.exceptions import ValidationError

from .auth_helpers import ensure_authenticated_user
from .models import ChatMessage, Follow, StreamSession, User, Video, VideoReaction


def _lock_users(*user_ids):
    list(
        User.objects.select_for_update()
        .filter(id__in=user_ids)
        .order_by('id')
        .values_list('id', flat=True)
    )


def _sync_follow_counts(*, follower_id, following_id):
    User.objects.filter(id=follower_id).update(
        following_count=Follow.objects.filter(follower_id=follower_id).count()
    )
    User.objects.filter(id=following_id).update(
        followers_count=Follow.objects.filter(following_id=following_id).count()
    )


@transaction.atomic
def create_follow(*, follower, following):
    follower = ensure_authenticated_user(follower)

    if follower == following:
        raise ValidationError({'is_following': 'Users may not follow themselves.'})

    _lock_users(follower.id, following.id)
    Follow.objects.get_or_create(follower=follower, following=following)
    _sync_follow_counts(follower_id=follower.id, following_id=following.id)


@transaction.atomic
def delete_follow(*, follower, following):
    follower = ensure_authenticated_user(follower)

    _lock_users(follower.id, following.id)
    Follow.objects.filter(follower=follower, following=following).delete()
    _sync_follow_counts(follower_id=follower.id, following_id=following.id)


def _sync_reaction_counts(*, video_id):
    counts = {
        row['reaction']: row['total']
        for row in VideoReaction.objects.filter(video_id=video_id)
        .values('reaction')
        .annotate(total=Count('id'))
    }

    Video.objects.filter(id=video_id).update(
        like_count=counts.get(VideoReaction.LIKE, 0),
        dislike_count=counts.get(VideoReaction.DISLIKE, 0),
    )


@transaction.atomic
def set_video_reaction(*, user, video, reaction):
    user = ensure_authenticated_user(user)

    Video.objects.select_for_update().get(id=video.id)
    VideoReaction.objects.update_or_create(
        user=user,
        video=video,
        defaults={'reaction': reaction},
    )
    _sync_reaction_counts(video_id=video.id)


@transaction.atomic
def clear_video_reaction(*, user, video):
    user = ensure_authenticated_user(user)

    Video.objects.select_for_update().get(id=video.id)
    reaction = VideoReaction.objects.select_for_update().filter(
        user=user,
        video=video,
    ).first()

    if reaction is None:
        return

    reaction.delete()
    _sync_reaction_counts(video_id=video.id)


def _get_active_stream_session_for_message(*, video_id):
    stream_session = StreamSession.objects.select_related('video').select_for_update().filter(
        video_id=video_id,
        is_live=True,
    ).first()

    if stream_session is None:
        raise ValidationError({'video': ['Live session not found.']})

    return stream_session


@transaction.atomic
def create_video_message(*, user, message, video_id):
    user = ensure_authenticated_user(user)
    stream_session = _get_active_stream_session_for_message(video_id=video_id)
    return ChatMessage.objects.create(
        user=user,
        video=stream_session.video,
        message=message,
    )