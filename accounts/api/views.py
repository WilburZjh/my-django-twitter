from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from accounts.api.serializers import UserSerializer

# design an User API to view and modify User table in DataBase.
# /api/user/ -> all users
# /api/user/id/ -> id user
# permission_classes -> 针对每一个操作进行一个检测，检测是用户是否登录，没登录就不能做任何事情。
class UserViewSet(viewsets.ModelViewSet):
    # 1.怎么渲染数据（数据怎么变成json），
    # 2.有一个默认的表单，根据这个serializer去创建，这样在Django-rest-framework这个界面去进行数据的提交
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
