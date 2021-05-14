from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    # FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User

class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all ()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object()
    # 也就是 queryset.filter(pk=1) 查询一下这个 object 在不在
    queryset = User.objects.all()

    # 我的粉丝
    # detail=True会验证pk存不存在，若pk不存在，则会报404
    # 这个默认的验证机制会调用self.get_object() ->这个方法会去取self.get_queryset()
    # GET api/friendships/pk/followers/ -> 看用户pk的followers
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships=Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer=FollowerSerializer(friendships, many=True)
        return Response({
            'followers': serializer.data,
        }, status=status.HTTP_200_OK,)

    # 必须定义list函数，否则访问localhost的时候将看不到api/friendships
    # 实现localhost/api/friendships/?from_user_id=1，需要重写list函数。
    def list(self, request):
        return Response({'message' : 'this is friendship home page.'})

    # 我关注了哪些人
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response(
            {'followings': serializer.data},
            status=status.HTTP_200_OK,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        pass

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        pass


