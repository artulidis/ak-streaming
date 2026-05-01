from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AccountStreamKey, ChatMessage, StreamSession, Topic, Video

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'display_name',
            'avatar_url',
        )
        read_only_fields = fields

    def get_avatar_url(self, obj):
        if not obj.avatar:
            return ''
        return self._build_media_url(obj.avatar.url)

    def _build_media_url(self, path):
        if not path:
            return ''
        request = self.context.get('request')
        if request is None:
            return path
        return request.build_absolute_uri(path)


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True, 'trim_whitespace': False},
        }

    def validate_password(self, value):
        user = User(
            username=self.initial_data.get('username', ''),
        )
        validate_password(value, user=user)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'display_name',
            'bio',
            'avatar_url',
            'followers_count',
            'following_count',
        )
        read_only_fields = (
            'id',
            'username',
            'followers_count',
            'following_count',
        )

    def get_avatar_url(self, obj):
        return UserSummarySerializer(context=self.context).get_avatar_url(obj)


class UserProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'display_name',
            'bio',
            'avatar',
        )


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'id',
            'name',
        )
        read_only_fields = fields

    def validate_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Topic name cannot be blank.')
        return cleaned_value


class VideoListSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'user',
            'name',
            'views',
            'like_count',
            'dislike_count',
            'topics',
            'thumbnail',
            'created',
        )
        read_only_fields = fields


class VideoDetailSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'user',
            'name',
            'description',
            'views',
            'like_count',
            'dislike_count',
            'topics',
            'thumbnail',
            'created',
        )
        read_only_fields = fields


class VideoWriteSerializer(serializers.ModelSerializer):
    topic_names = serializers.SlugRelatedField(
        source='topics',
        many=True,
        slug_field='name',
        queryset=Topic.objects.all(),
        required=False,
    )

    class Meta:
        model = Video
        fields = (
            'name',
            'description',
            'topic_names',
            'thumbnail',
        )

    def validate_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Video name cannot be blank.')
        return cleaned_value


class UserFollowStateSerializer(serializers.Serializer):
    is_following = serializers.BooleanField(read_only=True)


class VideoReactionStateSerializer(serializers.Serializer):
    reaction = serializers.ChoiceField(
        choices=(('like', 'like'), ('dislike', 'dislike')),
        allow_null=True,
        required=False,
    )


class VideoReactionWriteSerializer(serializers.Serializer):
    reaction = serializers.ChoiceField(choices=(('like', 'like'), ('dislike', 'dislike')))


class StreamSessionReadSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    hls_url = serializers.SerializerMethodField()
    recording_url = serializers.SerializerMethodField()

    class Meta:
        model = StreamSession
        fields = (
            'id',
            'user',
            'video',
            'playback_id',
            'is_live',
            'started_at',
            'ended_at',
            'hls_url',
            'recording_url',
        )
        read_only_fields = fields

    def get_hls_url(self, obj):
        return self._build_stream_url(f'/stream/hls/{obj.playback_id}.m3u8')

    def get_recording_url(self, obj):
        return self._build_stream_url(f'/stream/rec/{obj.playback_id}.mp4')

    def _build_stream_url(self, path):
        request = self.context.get('request')
        if request is None:
            return path
        return request.build_absolute_uri(path)


class AccountStreamKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountStreamKey
        fields = (
            'stream_key_last4',
            'rotated_at',
        )
        read_only_fields = fields


class AccountStreamKeyRotateResponseSerializer(AccountStreamKeySerializer):
    stream_key = serializers.CharField(read_only=True)

    class Meta(AccountStreamKeySerializer.Meta):
        fields = (
            'stream_key',
            'stream_key_last4',
            'rotated_at',
        )


class ChatMessageReadSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'user',
            'message',
            'created_at',
        )
        read_only_fields = fields


class ChatMessageWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ('message',)

    def validate_message(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Message cannot be blank.')
        return cleaned_value