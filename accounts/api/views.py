from django.contrib.auth.models import User
from django.contrib.auth import (
    login as django_login,
    logout as django_logout,
    authenticate as django_authenticate,
)
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer,
)

# design an User API to view and modify User table in DataBase.
# /api/user/ -> all users
# /api/user/id/ -> id user
# permission_classes: 对操作进行检测，检测用户是否登录，若没有登录则无法进行任何操作。
class UserViewSet(viewsets.ModelViewSet):
    # 1.怎么渲染数据（数据怎么变成json），
    # 2.有一个默认的表单，根据这个serializer去创建，这样在Django-rest-framework这个界面去进行数据的提交
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer

    # 1. localhost/api/accounts/1/login_status/ 必须要带着userID才能访问。
    # @action(methods=['GET'], detail=True)
    # def login_status(self, request, pk):
    #     data ={
    #         'has_logged_in':request.user.is_authenticated,
    #     }
    #     if request.user.is_authenticated:
    #         data['user'] = UserSerializer(request.user).data
    #     return Response(data)

    # 2. localhost/api/accounts/login_status/ 无须userID，全局状态查看。
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data ={
            'has_logged_in':request.user.is_authenticated,
            'ip':request.META['REMOTE_ADDR']
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({"success": True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # get username and password from request,
        # 直接这么写有问题，因为无法保证用户传入了username和password。
        # request.data['username']
        # request.data['password']
        # 这时就需要定义一个serializer来验证用户的输入。

        # data是用户请求的数据，从request.data拿到的。
        # 若是一个get请求，则 data=request.query_params
        serializer = LoginSerializer(data=request.data)
        #查看username和password是否存在
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 验证用户不存在
        if not User.objects.filter(username=username).exists():
            return Response({
                "success": False,
                "message": "User does not exist.",
            }, status=400)

        user = django_authenticate(username=username, password=password)
        # 判断user是否为空或者anonymous
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match.",
            }, status=400)

        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input.",
                "errors": serializer.errors,
            }, status=400)

        # 会创建出一个user
        user = serializer.save()
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(user).data,
        }, status=201)
