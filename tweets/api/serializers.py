from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer, UserSerializerForTweet
from comments.api.serializers import CommentSerializer

class TweetListSerializer(serializers.ModelSerializer):
    user=UserSerializerForTweet()

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerWithComments(TweetListSerializer):
    user = UserSerializer()
    # <HOMEWORK> 使用 serialziers.SerializerMethodField 的方式实现 comments
    comments = CommentSerializer(source='comment_set', many=True)

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'comments', 'created_at', 'content')

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
