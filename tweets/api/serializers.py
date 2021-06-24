from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer, UserSerializerForTweet
from comments.api.serializers import CommentSerializer
from likes.services import LikeService
from likes.api.serializers import LikeSerializer

class TweetListSerializer(serializers.ModelSerializer):
    user=UserSerializerForTweet()
    comments_count = serializers.SerializerMethodField() # 定义了一个完全自定义的return格式
    likes_count = serializers.SerializerMethodField()
    has_liked=serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

class TweetSerializerForDetail(TweetListSerializer):
    # user = UserSerializer()
    # <HOMEWORK> 使用 serialziers.SerializerMethodField 的方式实现 comments
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'comments',
            'created_at',
            'content',
            'likes',
            'comments',
            'likes_count',
            'comments_count',
            'has_liked',
        )

class TweetCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model=Tweet # 指定对应的是哪个model
        fields=('content',)

    """
    重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
    """
    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
