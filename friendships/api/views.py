from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.paginations import FriendshipPagination
from friendships.api.serializers import (
    FollowingSerializer,
    FollowerSerializer,
    FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User
from friendships.services import FriendshipService


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all ()
    # 如果是 Friendship.objects.all 的话就会出现 404 Not Found
    # 因为 detail=True 的 actions 会默认先去调用 get_object()
    # 也就是 queryset.filter(pk=1) 查询一下这个 object 在不在
    queryset = User.objects.all()
    serializer_class = FriendshipSerializerForCreate # POST方法需要指定一个serializer_class
    pagination_class = FriendshipPagination

    # 我的粉丝
    # detail=True会验证pk存不存在，若pk不存在，则会报404
    # 这个默认的验证机制会调用self.get_object() ->这个方法会去取self.get_queryset()
    # GET api/friendships/pk/followers/ -> 看用户pk的followers
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # http://localhost/api/friendships/1/followers/?page=1
        # 这个friendships是所有的数据，但是我们需要根据request里面指定的参数去决定要显示哪些数据。
        friendships=Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        """
        Paginator是看看有没有设定pagination class
        Return a single page of results, or `None` if pagination is disabled.
        """
        # This is friendships ------>
        # < QuerySet[ < Friendship: 6 followed 7 >, < Friendship: 1 followed 7 >, < Friendship: 5 followed 7 >] >
        # 于是就需要将friendships传给paginate_queryset去根绝request里面的params进行筛选。
        page=self.paginate_queryset(friendships)

        # print('This is page {}:'.format(page))
        # This is page ------->
        # < QuerySet[ < Friendship: 6 followed 7 >, < Friendship: 1 followed 7 >, < Friendship: 5 followed 7 >] >
        serializer=FollowerSerializer(
            page,
            context={'request': request},
            many=True,
        )
        # return Response({
        #     'followers': serializer.data,
        # }, status=status.HTTP_200_OK,)

        # 因为指定了pagination_class，因此self.paginator会变成FriendshipPagination()。
        # self.get_paginated_response()会调用FriendshipPagination().get_paginated_response(data)。
        # 对Response再次进行封装。
        return self.get_paginated_response(serializer.data)

    # 必须定义list函数，否则访问localhost的时候将看不到api/friendships
    # 实现localhost/api/friendships/?from_user_id=1，需要重写list函数。
    def list(self, request):
        return Response({'message' : 'this is friendship home page.'})

    # 我关注了哪些人
    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(page, context={'request': request}, many=True)
        # return Response(
        #     {'followings': serializer.data},
        #     status=status.HTTP_200_OK,
        # )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        # 检测pk是否存在
        self.get_object() #: 返回404

        # api/friendships/pk/follow/
        # 特殊判断重复 follow 的情况（比如前端猛点好多少次 follow)
        # 静默处理，不报错，因为这类重复操作因为网络延迟的原因会比较多，没必要当做错误处理
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'success': True,
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)
        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id, # 当前用户
            'to_user_id': pk, # 我要去关注的用户
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        FriendshipService.invalidate_following_cache(request.user.id)
        return Response(
            FollowingSerializer(
                instance,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        self.get_object()
        # 注意 pk 的类型是 str，所以要做类型转换
        if request.user.id == int(pk):
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself',
            }, status=status.HTTP_400_BAD_REQUEST)
        # https://docs.djangoproject.com/en/3.1/ref/models/querysets/#delete
        # Queryset 的 delete 操作返回两个值，一个是删了多少数据，一个是具体每种类型删了多少
        # 为什么会出现多种类型数据的删除？因为可能因为 foreign key 设置了 cascade 出现级联
        # 删除，也就是比如 A model 的某个属性是 B model 的 foreign key，并且设置了
        # on_delete=models.CASCADE, 那么当 B 的某个数据被删除的时候，A 中的关联也会被删除。
        # 所以 CASCADE 是很危险的，我们一般最好不要用，而是用 on_delete=models.SET_NULL
        # 取而代之，这样至少可以避免误删除操作带来的多米诺效应。
        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=pk,
        ).delete()
        FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success': True, 'deleted': deleted})

