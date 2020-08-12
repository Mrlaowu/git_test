from django.db import models

class BaseModel(models.Model):
    """模型类抽象基类"""
    #创建时间
    create_time=models.DateField(auto_now_add=True,verbose_name="创建时间")
    #更新时间
    update_time=models.DateField(auto_now=True,verbose_name="更新时间")
    #删除标识
    is_delete=models.BooleanField(default=True,verbose_name="删除标记")

    class Meta:
        #说明是一个抽象模型类
        abstract=True