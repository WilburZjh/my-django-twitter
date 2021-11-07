from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.models import NewsFeed
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper
from newsfeeds.tasks import fanout_newsfeeds_main_task


class NewsFeedService(object):

    @classmethod
    def fanout_to_followers(cls, tweet): # fanout指的是将tweet分发给我的followers。
        # # 错误的方法
        # # 不可以将数据库操作放在 for 循环里面，效率会非常低
        # # for follower in FriendshipService.get_followers(tweet.user):
        # #     NewsFeed.objects.create(
        # #         user=follower,
        # #         tweet=tweet,
        # #     )
        #
        # # 正确的方法：使用 bulk_create，会把 insert 语句合成一条
        # newsfeeds = [
        #     NewsFeed(user=follower, tweet=tweet) # 还没产生数据库的存储因为并没有.save()
        #     for follower in FriendshipService.get_followers(tweet.user)
        # ]
        # # 自己发的自己也能看到。
        # newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        # NewsFeed.objects.bulk_create(newsfeeds)
        #
        # # bulk create 不会触发 post_save 的 signal，所以需要手动 push 到 cache 里
        # for newsfeed in newsfeeds:
        #     cls.push_newsfeed_to_cache(newsfeed)

        # =======================================================================
        # 这句话的作用是，在 celery 配置的 message queue 中创建一个 fanout 的任务
        # 参数是 tweet。任意一个在监听 message queue 的 worker 进程都有机会拿到这个任务
        # worker 进程中会执行 fanout_newsfeeds_task 里的代码来实现一个异步的任务处理
        # 如果这个任务需要处理 10s 则这 10s 会花费在 worker 进程上，而不是花费在用户发 tweet
        # 的过程中。所以这里 .delay 操作会马上执行马上结束从而不影响用户的正常操作。
        # （因为这里只是创建了一个任务，把任务信息放在了 message queue 里，并没有真正执行这个函数）
        # 要注意的是，delay 里的参数必须是可以被 celery serialize 的值，因为 worker 进程是一个独立
        # 的进程，甚至在不同的机器上，没有办法知道当前 web 进程的某片内存空间里的值是什么。所以
        # 我们只能把 tweet.id 作为参数传进去，而不能把 tweet 传进去。因为 celery 并不知道
        # 如何 serialize Tweet。

        # fanout_newsfeeds_task.delay(tweet.id) # 异步任务
        # fanout_newsfeeds_task(tweet.id)  # 同步任务

        fanout_newsfeeds_main_task.delay(tweet.id, tweet.user_id)

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
