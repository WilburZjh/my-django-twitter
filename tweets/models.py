from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now

# https://stackoverflow.com/questions/35129697/difference-between-model-fieldsin-django-and-serializer-fieldsin-django-rest
# Create your models here.
class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="This user refers to the user who posts this tweet.",
        verbose_name=u"谁发了这个帖子",
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) # 有时区（vagrant/server所在的时区）

    class Meta:
        # 联合索引 compound index/composite index
        # 相当于在数据库中建立了一个我看不到的表单，这个表单中一共有3列。
        # [
        #   ('user', 'created_at', 'id'),
        #   ...
        # ]

        # 建立了索引也要进行makemigration和migrate
        index_together = (
            ('user', 'created_at'),
        )

        # ordering 不会对数据库产生影响。
        ordering = ('user', '-created_at')



    @property
    def hours_to_now(self):
        # datetime.now()不带时区信息，需要增加上utc的时区信息。
        return (utc_now()-self.created_at).seconds // 3600

    def __str__(self):
        # 当执行 print(tweet instance) 的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'