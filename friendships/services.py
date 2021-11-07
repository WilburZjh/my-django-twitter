from django.conf import settings
from django.core.cache import caches
from friendships.models import Friendship
from twitter.cache import FOLLOWINGS_PATTERN

cache = caches['testing'] if settings.TESTING else caches['default']

class FriendshipService(object):

    @classmethod
    def get_followers(cls, user):
        # 错误的写法一
        # 这种写法会导致 N + 1 Queries 的问题
        # 即，filter 出所有 friendships 耗费了一次 Query
        # 而 for 循环每个 friendship 取 from_user 又耗费了 N 次 Queries
        # friendships = Friendship.objects.filter(to_user=user)
        # return [friendship.from_user for friendship in friendships]

        # 错误的写法二
        # 这种写法是使用了 JOIN 操作，让 friendship table 和 user table 在 from_user
        # 这个属性上 join 了起来。join 操作在大规模用户的 web 场景下是禁用的，因为非常慢。
        # friendships = Friendship.objects.filter(
        #     to_user=user
        # ).select_related('from_user')
        # return [friendship.from_user for friendship in friendships]

        # 正确的写法一，自己手动 filter id，使用 IN Query 查询
        # friendships = Friendship.objects.filter(to_user=user)
        # friendship.from_user_id并不会产生新的query。
        # follower_ids = [friendship.from_user_id for friendship in friendships]
        # followers = User.objects.filter(id__in=follower_ids)

        # 正确的写法二，使用 prefetch_related，会自动执行成两条语句，用 In Query 查询
        # 实际执行的 SQL 查询和上面是一样的，一共两条 SQL Queries
        friendships = Friendship.objects.filter(
            to_user=user,
        ).prefetch_related('from_user')
        return [friendship.from_user for friendship in friendships]

    @classmethod
    def get_follower_ids(cls, to_user_id):
        friendships = Friendship.objects.filter(to_user_id=to_user_id)
        return [friendship.from_user_id for friendship in friendships]


    @classmethod
    # def has_followed(cls, user, target):
    #     return Friendship.objects.filter(
    #         from_user=user,
    #         to_user=target,
    #     ).exists()
    def get_following_user_id_set(cls, from_user_id):
        # memcached的缓存。就是如果有多台 web 服务器，每台都访问同一个 memcached
        # 根据当前user_id去算出他在memcached中的key是什么
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        user_id_set = cache.get(key)
        if user_id_set is not None:
            return user_id_set

        friendships = Friendship.objects.filter(from_user_id=from_user_id)
        user_id_set = set([
            fs.to_user_id
            for fs in friendships
        ])
        cache.set(key, user_id_set)
        return user_id_set

    # 当 Friendship 有增加或者删除的时候会调用。
    # 只有访问 localhost/api/friendships/1/follow 的时候才会有用，如果访问的是 localhost/admin 则是无效的。
    # 可以通过使用 listener 的机制来使得访问 localhost/admin 的时候也是有效的。
    @classmethod
    def invalidate_following_cache(cls, from_user_id):
        key = FOLLOWINGS_PATTERN.format(user_id=from_user_id)
        cache.delete(key)
