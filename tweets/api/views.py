from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tweets.api.serializers import TweetListSerializer, TweetCreateSerializer
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService

# ModelViewSet ： 默认 增删查改 都可以做, 所以这样不太合适。
# 很多时候，我们的接口并不是总允许 给非admin的人 权限进行 增删改 操作
# class TweetViewSet(viewsets.ModelViewSet):

class TweetViewSet(viewsets.GenericViewSet):
    # queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    # 这个函数
    def get_permissions(self):
        if self.action == 'list': # action: list, create
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request):
        """
        重载 list 方法，不列出所有 tweets，必须要求指定 user_id 作为筛选条件
        """
        if 'user_id' not in request.query_params:
            return Response('missing user id', status=400)

        # 这句查询会被翻译为
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # 这句 SQL 查询会用到 user 和 created_at 的联合索引
        # 单纯的 user 索引是不够的
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        # 将找出来的tweets传给serializer
        serializer = TweetListSerializer(tweets, many=True) # 会返回一个list of dict, 每一个的dict都是一个TweetListSerializer

        # 一般来说 json 格式的 response 默认都要用 hash 的格式
        # 而不能用 list 的格式（约定俗成）
        return Response({'tweets': serializer.data})

    def create(self, request):
        """
        重载 create 方法，因为需要默认用当前登录用户作为 tweet.user
        """
        serializer = TweetCreateSerializer(
            data=request.data, # 用户post的data
            context={'request': request}, # 额外的信息
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=400)

        # 这个save()函数将会调用TweetCreateSerializer中的create()的方法。
        # 返回的是django的一个ORM的object。
        tweet=serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        # 展示tweet和创建tweet的时候分别使用两个不同的serializer。
        return Response(TweetListSerializer(tweet).data, status=201)
