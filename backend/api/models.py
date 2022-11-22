from argparse import ONE_OR_MORE
from doctest import BLANKLINE_MARKER
from typing_extensions import Self
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

def upload_to(instance, filename):
    return f'profile_images/{filename}'.format(filename=filename)


class MyUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(
            username=username
        )
        user.is_active=True
        user.is_superuser=False
        user.is_staff=False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username=username,
            password=password,
        )
        user.is_active=True
        user.is_superuser=True
        user.is_staff=True
        user.save()
        return user

class MyUser(AbstractBaseUser):
    objects = MyUserManager()
    class Meta:
        db_table = 'user_entity'

    id = models.AutoField(primary_key=True, db_column='userId')
    username = models.CharField(db_column='username', unique=True, max_length=20)
    password = models.CharField(db_column='password', max_length=256)
    email = models.EmailField(max_length=256, blank=True, null=True)
    full_name = models.CharField(db_column='full_name', max_length=40, null=True, blank=True)
    profile_image = models.ImageField(db_column='profile_image', upload_to=upload_to, null=True, blank=True)
    followers = models.IntegerField(db_column='followers', validators=[MinValueValidator(0)], null=True, blank=True)
    bio = models.TextField(db_column='bio', max_length=256, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    def __str__(self):
        return str(self.username)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class UserFollowingCount(models.Model):
    owner = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='owner')
    users = models.ManyToManyField(MyUser, blank=True, null=True, related_name='user')



class WatchList(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=False, null=True)

    def __str__(self):
        return f"{self.name}"


class Topic(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


class Video(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True,)
    name = models.CharField(max_length=100, blank=False, null=True)
    likes = models.ManyToManyField(MyUser, null=True, blank=True, related_name='users_liked')
    dislikes = models.ManyToManyField(MyUser, null=True, blank=True, related_name='users_disliked')
    stream_key = models.CharField(max_length=1000, blank=False, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True) 
    views = models.IntegerField(validators=[MinValueValidator(0)], default=0, blank=False, null=True)
    topics = models.ManyToManyField(Topic, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} : {self.user}"



class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField(max_length=1000, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.body}"   
