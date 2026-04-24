from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def end_duplicate_live_sessions(apps, schema_editor):
    StreamSession = apps.get_model('api', 'StreamSession')

    live_sessions = StreamSession.objects.filter(is_live=True).order_by('-started_at', '-id')
    seen_user_ids = set()
    seen_video_ids = set()
    session_ids_to_end = []

    for stream_session in live_sessions.iterator():
        if stream_session.user_id in seen_user_ids or stream_session.video_id in seen_video_ids:
            session_ids_to_end.append(stream_session.id)
            continue

        seen_user_ids.add(stream_session.user_id)
        seen_video_ids.add(stream_session.video_id)

    if session_ids_to_end:
        StreamSession.objects.filter(id__in=session_ids_to_end).update(
            is_live=False,
            ended_at=django.utils.timezone.now(),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountStreamKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stream_key_hash', models.CharField(max_length=255)),
                ('stream_key_last4', models.CharField(max_length=4)),
                ('rotated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='account_stream_key', to='api.user')),
            ],
        ),
        migrations.RenameField(
            model_name='streamsession',
            old_name='stream_key',
            new_name='playback_id',
        ),
        migrations.AddField(
            model_name='streamsession',
            name='ended_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(end_duplicate_live_sessions, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='streamsession',
            constraint=models.UniqueConstraint(condition=models.Q(('is_live', True)), fields=('user',), name='unique_live_stream_session_per_user'),
        ),
        migrations.AddConstraint(
            model_name='streamsession',
            constraint=models.UniqueConstraint(condition=models.Q(('is_live', True)), fields=('video',), name='unique_live_stream_session_per_video'),
        ),
    ]