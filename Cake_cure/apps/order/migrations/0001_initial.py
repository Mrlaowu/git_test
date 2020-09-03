# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cake', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCake',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('detele_time', models.BooleanField(verbose_name='删除标记', default=True)),
                ('count', models.IntegerField(verbose_name='商品数目', default=1)),
                ('price', models.IntegerField(verbose_name='商品价格')),
            ],
            options={
                'verbose_name': '订单商品',
                'verbose_name_plural': '订单商品',
                'db_table': 'df_order_cake',
            },
        ),
        migrations.CreateModel(
            name='Orderinfo',
            fields=[
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('detele_time', models.BooleanField(verbose_name='删除标记', default=True)),
                ('order_id', models.CharField(primary_key=True, max_length=128, serialize=False)),
                ('total_count', models.IntegerField(verbose_name='商品总数量', default=1)),
                ('total_price', models.IntegerField(verbose_name='商品总价格')),
                ('transit_price', models.IntegerField(verbose_name='运费', default=10)),
                ('order_status', models.SmallIntegerField(verbose_name='订单状态', default=1, choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')])),
                ('addr', models.ForeignKey(verbose_name='地址', to='user.Address')),
                ('user', models.ForeignKey(verbose_name='用户', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'db_table': 'df_order_info',
            },
        ),
        migrations.AddField(
            model_name='ordercake',
            name='order',
            field=models.ForeignKey(verbose_name='订单', to='order.Orderinfo'),
        ),
        migrations.AddField(
            model_name='ordercake',
            name='sku',
            field=models.ForeignKey(verbose_name='商品sku', to='cake.Cake_Sku'),
        ),
    ]
