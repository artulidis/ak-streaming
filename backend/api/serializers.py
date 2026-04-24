from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
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

    def validate_password(self, value):
        user = User(
            username=self.initial_data.get('username', ''),
            email=self.initial_data.get('email', ''),
        )
        validate_password(value, user=user)
        return value

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


class UserProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'display_name',
            'bio',
            'avatar_url',
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
    topic_ids = serializers.PrimaryKeyRelatedField(
        source='topics',
        many=True,
        queryset=Topic.objects.all(),
        required=False,
    )

    class Meta:
        model = Video
        fields = (
            'name',
            'description',
            'topic_ids',
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