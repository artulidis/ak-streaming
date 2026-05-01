from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import NotFound, ValidationError

from .auth_helpers import ensure_authenticated_user
from .models import ChatMessage, Follow, StreamSession, User, Video, VideoReaction


def _lock_users(*user_ids):
    list(
        User.objects.select_for_update()
        .filter(id__in=user_ids)
        .order_by('id')
        .values_list('id', flat=True)
    )


def _increment_follow_counts(*, follower_id, following_id):
    User.objects.filter(id=follower_id).update(
        following_count=F('following_count') + 1
    )
    User.objects.filter(id=following_id).update(
        followers_count=F('followers_count') + 1
    )


def _decrement_follow_counts(*, follower_id, following_id):
    User.objects.filter(id=follower_id).update(
        following_count=F('following_count') - 1
    )
    User.objects.filter(id=following_id).update(
        followers_count=F('followers_count') - 1
    )


@transaction.atomic
def create_follow(*, follower, following):
    follower = ensure_authenticated_user(follower)

    if follower == following:
        raise ValidationError({'is_following': 'Users may not follow themselves.'})

    _lock_users(follower.id, following.id)
    _, created = Follow.objects.get_or_create(follower=follower, following=following)

    if created:
        _increment_follow_counts(follower_id=follower.id, following_id=following.id)


@transaction.atomic
def delete_follow(*, follower, following):
    follower = ensure_authenticated_user(follower)

    _lock_users(follower.id, following.id)
    deleted_count, _ = Follow.objects.filter(follower=follower, following=following).delete()

    if deleted_count:
        _decrement_follow_counts(follower_id=follower.id, following_id=following.id)


def _apply_video_reaction_count_delta(*, video_id, like_delta=0, dislike_delta=0):
    updates = {}

    if like_delta:
        updates['like_count'] = F('like_count') + like_delta
    if dislike_delta:
        updates['dislike_count'] = F('dislike_count') + dislike_delta

    if updates:
        Video.objects.filter(id=video_id).update(**updates)


@transaction.atomic
def set_video_reaction(*, user, video, reaction):
    user = ensure_authenticated_user(user)

    Video.objects.select_for_update().get(id=video.id)
    current_reaction = VideoReaction.objects.select_for_update().filter(
        user=user,
        video=video,
    ).first()

    if current_reaction is None:
        VideoReaction.objects.create(user=user, video=video, reaction=reaction)
        _apply_video_reaction_count_delta(
            video_id=video.id,
            like_delta=1 if reaction == VideoReaction.LIKE else 0,
            dislike_delta=1 if reaction == VideoReaction.DISLIKE else 0,
        )
        return

    if current_reaction.reaction == reaction:
        return

    previous_reaction = current_reaction.reaction
    current_reaction.reaction = reaction
    current_reaction.save(update_fields=['reaction'])
    _apply_video_reaction_count_delta(
        video_id=video.id,
        like_delta=(1 if reaction == VideoReaction.LIKE else 0) - (
            1 if previous_reaction == VideoReaction.LIKE else 0
        ),
        dislike_delta=(1 if reaction == VideoReaction.DISLIKE else 0) - (
            1 if previous_reaction == VideoReaction.DISLIKE else 0
        ),
    )


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

    reaction_value = reaction.reaction
    reaction.delete()
    _apply_video_reaction_count_delta(
        video_id=video.id,
        like_delta=-1 if reaction_value == VideoReaction.LIKE else 0,
        dislike_delta=-1 if reaction_value == VideoReaction.DISLIKE else 0,
    )


def _get_active_stream_session_for_message(*, video_id):
    stream_session = StreamSession.objects.select_related('video').select_for_update().filter(
        video_id=video_id,
        is_live=True,
    ).first()

    if stream_session is None:
        raise NotFound('No active stream session was found for this video.')

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