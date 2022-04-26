from rest_framework import serializers
from .models import UserInfo


class UserInfoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo  # 序列化哪个 模型对象的字段
        fields = '__all__'



