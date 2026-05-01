from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_account_stream_keys_and_stream_sessions'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='avatars/'),
        ),
        migrations.RemoveField(
            model_name='user',
            name='avatar_url',
        ),
    ]