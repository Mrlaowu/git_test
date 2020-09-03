from django.db import models
from db.basemodel import BaseModel
from tinymce.models import HTMLField

class Cake_Sku(BaseModel):
    """商品sku模型类"""
    type=models.ForeignKey("CakeType",verbose_name="商品种类")
    cake_spu=models.ForeignKey("Cake_Spu",verbose_name="商品Spu")
    name=models.CharField(max_length=10,verbose_name="商品名称")
    price=models.IntegerField(verbose_name="商品价格")
    unit=models.CharField(max_length=10,verbose_name="单位")
    stock=models.IntegerField(verbose_name="库存")
    image=models.ImageField(upload_to="apps",verbose_name="图片")
    desc=models.CharField(max_length=256,verbose_name="商品简述")

    class Meta:
        db_table="df_cake_sku"
        verbose_name="商品"
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name

class Cake_Spu(BaseModel):
    """商品Spu模型表"""
    name=models.CharField(max_length=20,verbose_name="商品spu名称")
    #富文本模型
    detail=HTMLField(blank=True,verbose_name="商品详情")

    class Meta:
        db_table="df_cake_spu"
        verbose_name="商品Spu"
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name

class CakeType(BaseModel):
    """商品种类"""
    name=models.CharField(max_length=10,verbose_name="商品种类名称")

    class Meta:
        db_table="df_cake_type"
        verbose_name="商品种类"
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name
