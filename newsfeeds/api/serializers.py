from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetListSerializer


class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetListSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
