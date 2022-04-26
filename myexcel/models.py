from django.db import models

# Create your models here.
class UserInfo(models.Model):
    power_choice = (
        (0, 'false'),
        (1, 'true')
    )

    user_name = models.CharField(max_length=20, verbose_name='用户名')
    cn_name = models.CharField(max_length=20,verbose_name='域账户')
    power = models.SmallIntegerField(choices=power_choice, default=0, verbose_name='权限')


    class Meta:
        db_table = 'wx_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user_name
