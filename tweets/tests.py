from testing.testcases import TestCase
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):
    def setUp(self):
        self.linghu = self.create_user('linghu')
        self.tweet = self.create_tweet(self.linghu, content='Jiuzhang Dafa Hao')

    def test_hours_to_now(self):
        # linghu = User.objects.create_user(username='linghu')
        # tweet = Tweet.objects.create(user=linghu, content='Jiuzhang Dafa Good!')
        # tweet.created_at = utc_now() - timedelta(hours=10)
        # tweet.save()
        # self.assertEqual(tweet.hours_to_now, 10)
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like_set(self):
        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
