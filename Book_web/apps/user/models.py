from django.db import models
from db.basemodel import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser, BaseModel):
    """用户模型类"""

    def generate_acvite_token(self):
        """生成用户签名字符串"""
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': self.id}
        token = serializer.dumps(info)
        return token.decode()

    class Meta:
        db_table = "df_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

