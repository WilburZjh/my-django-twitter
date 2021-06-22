from django_filters.rest_framework import DjangoFilterBackend
from inbox.api.serializers import NotificationSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notifications.models import Notification

class NotificationViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin, # 列出get_queryset里面的所有的notifications, 里面有list的方法
):
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    filterset_fields = ('unread',) # 定义哪些项是可以被筛选的

    def get_queryset(self):
        return Notification.objects.filter(recipient = self.request.user)
        # return self.request.user.notifications.all()

    @action(methods=['GET'], detail=False, url_path='unread-count')
    def unread_count(self, request, *args, **kwargs):
        count = self.get_queryset().filter(unread=True).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='mark-all-as-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        updated_count = self.get_queryset().update(unread=False)
        return Response({'marked_count': updated_count}, status=status.HTTP_200_OK)
