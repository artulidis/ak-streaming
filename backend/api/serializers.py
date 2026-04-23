from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ChatMessage, Follow, StreamSession, Topic, Video, VideoReaction

User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'display_name',
            'avatar_url',
        )
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True, 'trim_whitespace': False},
            'email': {'required': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
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


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id',)

    def validate_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Topic name cannot be blank.')
        return cleaned_value


class VideoSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        source='topics',
        many=True,
        queryset=Topic.objects.all(),
        required=False,
        write_only=True,
    )

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
            'topic_ids',
            'thumbnail',
            'created',
        )
        read_only_fields = (
            'id',
            'user',
            'views',
            'like_count',
            'dislike_count',
            'created',
        )

    def validate_name(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Video name cannot be blank.')
        return cleaned_value


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSummarySerializer(read_only=True)
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
    )

    class Meta:
        model = Follow
        fields = (
            'id',
            'follower',
            'following',
            'created_at',
        )
        read_only_fields = (
            'id',
            'follower',
            'created_at',
        )

    def validate_following(self, value):
        request = self.context.get('request')
        if request and request.user.is_authenticated and value == request.user:
            raise serializers.ValidationError('Users may not follow themselves.')
        return value


class VideoReactionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = VideoReaction
        fields = (
            'id',
            'user',
            'video',
            'reaction',
            'created_at',
        )
        read_only_fields = (
            'id',
            'user',
            'created_at',
        )


class StreamSessionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = StreamSession
        fields = (
            'id',
            'user',
            'video',
            'is_live',
            'started_at',
        )
        read_only_fields = (
            'id',
            'user',
            'is_live',
            'started_at',
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = (
            'id',
            'video',
            'user',
            'message',
            'created_at',
        )
        read_only_fields = (
            'id',
            'user',
            'created_at',
        )

    def validate_message(self, value):
        cleaned_value = value.strip()
        if not cleaned_value:
            raise serializers.ValidationError('Message cannot be blank.')
        return cleaned_value