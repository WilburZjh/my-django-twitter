from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tweets.models import Tweet
from comments.models import Comment

class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        # 如果直接写 return APIClient() 则每次调用anonymous_client的时候都会new一个新的client。
        # 然而我只需要在第一次访问它的时候创建一个client就行了。
        # 设置了一个self的内部缓存：即instance level的一个cache。
        # queryset里面也有cache，和memorycachedb是不一样的。
        # 只要是同一个self/instance进来，就不会再重新生成。

        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client


    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)
