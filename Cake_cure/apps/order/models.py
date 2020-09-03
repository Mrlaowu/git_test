from django.db import models
from db.basemodel import  BaseModel

class Orderinfo(BaseModel):
    """订单信息模型类"""
    ORDER_STATUS={
        1:'待支付',
        2:'待发货',
        3:'待收货',
        4:"待评价",
        5:'已完成'
    }
    ORDER_STATUS_CHOICES=(
        (1,'待支付'),
        (2,'待发货'),
        (3,'待收货'),
        (4,'待评价'),
        (5,'已完成')
    )
    order_id=models.CharField(max_length=128,primary_key=True)
    addr=models.ForeignKey("user.Address",verbose_name="地址")
    user=models.ForeignKey("user.User",verbose_name="用户")
    total_count=models.IntegerField(default=1,verbose_name="商品总数量")
    total_price=models.IntegerField(verbose_name="商品总价格")
    transit_price=models.IntegerField(default=10,verbose_name="运费")
    order_status=models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,default=1,verbose_name="订单状态")

    class Meta:
        db_table='df_order_info'
        verbose_name="订单"
        verbose_name_plural=verbose_name

class OrderCake(BaseModel):
    """订单商品模型表"""
    order=models.ForeignKey("Orderinfo",verbose_name="订单")
    sku=models.ForeignKey("cake.Cake_Sku",verbose_name="商品sku")
    count=models.IntegerField(default=1,verbose_name="商品数目")
    price=models.IntegerField(verbose_name="商品价格")

    class Meta:
        db_table="df_order_cake"
        verbose_name="订单商品"
        verbose_name_plural=verbose_name