from newsfeeds.models import NewsFeed
from rest_framework import serializers
from tweets.api.serializers import TweetListSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetListSerializer(source='cached_tweet')

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
