# Generated by Django 4.1 on 2022-09-20 17:05

import api.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.AutoField(db_column='userId', primary_key=True, serialize=False)),
                ('username', models.CharField(db_column='username', max_length=20, unique=True)),
                ('password', models.CharField(db_column='password', max_length=256)),
                ('email', models.EmailField(blank=True, max_length=256, null=True)),
                ('full_name', models.CharField(blank=True, db_column='full_name', max_length=40, null=True)),
                ('profile_image', models.ImageField(blank=True, db_column='profile_image', null=True, upload_to=api.models.upload_to)),
                ('followers', models.IntegerField(blank=True, db_column='followers', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('bio', models.TextField(blank=True, db_column='bio', max_length=256, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user_entity',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('views', models.IntegerField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='thumbnails/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('dislikes', models.ManyToManyField(blank=True, null=True, related_name='users_disliked', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, null=True, related_name='users_liked', to=settings.AUTH_USER_MODEL)),
                ('topics', models.ManyToManyField(blank=True, null=True, to='api.topic')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFollowingCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, null=True, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField(blank=True, max_length=1000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.video')),
            ],
        ),
    ]
