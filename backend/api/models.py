from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, Index, Q, UniqueConstraint


class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=80, blank=True)
    bio = models.TextField(max_length=256, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)


class Follow(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['follower', 'following'], name='unique_follow_edge'),
            CheckConstraint(
                condition=~Q(follower=models.F('following')),
                name='prevent_self_follow',
            ),
        ]

    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_edges')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_edges')
    created_at = models.DateTimeField(auto_now_add=True)


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    class Meta:
        indexes = [
            Index(fields=['user', '-created']),
            Index(fields=['-created']),
        ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
    )

    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, blank=True)

    # Denormalized counters
    views = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    topics = models.ManyToManyField(Topic, related_name='videos', blank=True)

    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} : {self.user_id}"


class VideoReaction(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'video'], name='unique_user_video_reaction')
        ]
        indexes = [
            Index(fields=['video', 'reaction']),
        ]

    LIKE = 1
    DISLIKE = -1

    REACTION_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    reaction = models.SmallIntegerField(choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


class StreamSession(models.Model):
    class Meta:
        indexes = [
            Index(fields=['user', 'is_live']),
            Index(fields=['video', 'is_live']),
        ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    stream_key = models.CharField(max_length=255, unique=True)
    is_live = models.BooleanField(default=True)

    started_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    class Meta:
        indexes = [
            Index(fields=['video', '-created_at']),
        ]

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.message[:30]}"