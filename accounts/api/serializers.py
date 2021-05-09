from django.contrib.auth.models import User
from rest_framework import serializers

#所谓的serializer就是指定我要返回什么样的数据
#在localhost/api/users/ 会包含什么东西
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')
