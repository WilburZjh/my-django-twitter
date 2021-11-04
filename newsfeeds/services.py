from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet): # fanout指的是将tweet分发给我的followers。
        # 错误的方法
        # 不可以将数据库操作放在 for 循环里面，效率会非常低
        # for follower in FriendshipService.get_followers(tweet.user):
        #     NewsFeed.objects.create(
        #         user=follower,
        #         tweet=tweet,
        #     )

        # 正确的方法：使用 bulk_create，会把 insert 语句合成一条
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet) # 还没产生数据库的存储因为并没有.save()
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        # 自己发的自己也能看到。
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        NewsFeed.objects.bulk_create(newsfeeds)

        # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
        for newsfeed in newsfeeds:
            cls.push_newsfeed_to_cache(newsfeed)

    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)
