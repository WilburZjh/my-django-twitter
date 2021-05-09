from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import exceptions

# 所谓的serializer就是指定我要返回什么样的数据
# 在localhost/api/users/ 会包含什么东西
# 渲染用户的一个object
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

# Serializer的另一个用处是用来做验证用户的输入，做validation。
class LoginSerializer(serializers.Serializer):
    # 检查这两个默认存在的项是否有。
    username = serializers.CharField()
    password = serializers.CharField()

# 继承自ModelSerializer的时候，表示我这个field 最终serializer.save()的时候能够把这个用户实际的创建出来。
class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=6, max_length=20)
    password = serializers.CharField(min_length=6, max_length=20)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    # 还要验证，validate方法会在调用is_valid()的时候被调用
    def validate(self, data):
        if User.objects.filter(username=data['username'].lower()).exists():
            raise exceptions.ValidationError({
                "message": "This username has been occupied."
            })
        if User.objects.filter(email=data['email'].lower()).exists():
            raise exceptions.ValidationError({
                "message": "This email address has been occupied."
            })
        return data

    def create(self, validated_data):
        username=validated_data['username'].lower()
        email=validated_data['email'].lower()
        password=validated_data['password']

        # create_user将密码加密
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        return user
