from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import UniqueConstraint, Index


# ----------------------------
# User + Manager
# ----------------------------

class MyUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username=username, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    class Meta:
        db_table = 'user_entity'
        indexes = [
            Index(fields=['username']),
        ]

    id = models.BigAutoField(primary_key=True, db_column='userId')
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=256)

    email = models.EmailField(max_length=256, blank=True)
    full_name = models.CharField(max_length=40, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    bio = models.TextField(max_length=256, blank=True)

    # Denormalized counters
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()
    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


# ----------------------------
# Follow (Edge Table)
# ----------------------------

class Follow(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['follower', 'following'], name='unique_follow_edge')
        ]
        indexes = [
            Index(fields=['following']),  # for follower count lookups
            Index(fields=['follower']),   # for "who I follow"
        ]

    follower = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='following_edges')
    following = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='follower_edges')
    created_at = models.DateTimeField(auto_now_add=True)


# ----------------------------
# Topic
# ----------------------------

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        indexes = [
            Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


# ----------------------------
# Video
# ----------------------------

class Video(models.Model):
    class Meta:
        indexes = [
            Index(fields=['user', '-created']),   # fetch videos by user
            Index(fields=['-created']),           # feed ordering fallback
        ]

    user = models.ForeignKey(
        MyUser,
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

    topics = models.ManyToManyField(Topic, related_name='videos')

    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} : {self.user_id}"


# ----------------------------
# VideoReaction (Append-heavy)
# ----------------------------

class VideoReaction(models.Model):
    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'video'], name='unique_user_video_reaction')
        ]
        indexes = [
            Index(fields=['video', 'reaction']),  # fast aggregation
            Index(fields=['user']),               # "what did user like"
        ]

    LIKE = 1
    DISLIKE = -1

    REACTION_CHOICES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    reaction = models.SmallIntegerField(choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


# ----------------------------
# Stream Session (Ephemeral-ish)
# ----------------------------

class StreamSession(models.Model):
    class Meta:
        indexes = [
            Index(fields=['user', 'is_live']),
            Index(fields=['video', 'is_live']),
        ]

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)

    stream_key = models.CharField(max_length=255, unique=True)
    is_live = models.BooleanField(default=True)

    started_at = models.DateTimeField(auto_now_add=True)


# ----------------------------
# ChatMessage (Append-only)
# ----------------------------

class ChatMessage(models.Model):
    class Meta:
        indexes = [
            Index(fields=['video', '-created_at']),  # fetch recent chat
        ]

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}: {self.message[:30]}"