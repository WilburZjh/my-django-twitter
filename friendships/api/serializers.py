from accounts.api.serializers import UserSerializerForFriendship
from django.contrib.auth.models import User
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingUserIdSetMixin:

    # self: serializers.ModelSerializer => 是指定self的type必须是serializer.ModelSerializer
    # 获取PK的所有followers。单纯的内存查询，不会访问memcached
    @property
    def following_user_id_set(self: serializers.ModelSerializer):

        if self.context['request'].user.is_anonymous:
            return {}
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set
        # 根据当前登录用户的ID去获得缓存在memcached的所有关注的人
        user_id_set = FriendshipService.get_following_user_id_set(
            from_user_id=self.context['request'].user.id,
        )
        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


# serialize -> 把一个object变成一个string或者hash table。
# 可以通过 source=xxx 指定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
# 谁关注了我
class FollowerSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_from_user')
    has_followed = serializers.SerializerMethodField()

    class Meta:
        #
        model = Friendship
        # user来自from_user， 下面这个fields不是对应model里面的fields，会先去user = UserSerializer(source='from_user')这里面找。
        fields = ('user', 'created_at', 'has_followed') # 哪些人粉了我，何时粉的我。


    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢
        # return FriendshipService.has_followed(self.context['request'].user, obj.from_user)

        # optimized. list是O(N)，set是O(1)
        # 这个 follower 在不在我当前登录用户的关注者(following)的set中。
        # print('This is obj: {}; from_user_id: {}; to_user_id: {}'.format(obj, obj.from_user_id, obj.to_user_id))
        # This is obj: 6 followed 7; from_user_id: 6; to_user_id: 7
        # This is obj: 1 followed 7; from_user_id: 1; to_user_id: 7
        # This is obj: 5 followed 7; from_user_id: 5; to_user_id: 7

        return obj.from_user_id in self.following_user_id_set


# 我关注了谁
class FollowingSerializer(serializers.ModelSerializer, FollowingUserIdSetMixin):
    user = UserSerializerForFriendship(source='cached_to_user')
    # created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        # if self.context['request'].user.is_anonymous:
        #     return False
        # 这个部分会对每个 object 都去执行一次 SQL 查询，速度会很慢
        # return FriendshipService.has_followed(self.context['request'].user, obj.to_user)
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'from_user_id and to_user_id should be different.'
            })
        # if Friendship.objects.filter(
        #     from_user_id=attrs['from_user_id'],
        #     to_user_id=attrs['to_user_id'],
        # ).exists():
        #     raise ValidationError({
        #         'message': 'You already follow this user.'
        #     })

        # 检测PK是否存在。
        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You can not follow a non-existed user.'
            })
        return attrs

    def create(self, validated_data):
        from_user_id = validated_data['from_user_id']
        to_user_id = validated_data['to_user_id']
        return Friendship.objects.create(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
        )
