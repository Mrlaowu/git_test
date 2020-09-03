# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cake_Sku',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('detele_time', models.BooleanField(verbose_name='删除标记', default=True)),
                ('name', models.CharField(verbose_name='商品名称', max_length=10)),
                ('price', models.IntegerField(verbose_name='商品价格')),
                ('unit', models.CharField(verbose_name='单位', max_length=10)),
                ('stock', models.IntegerField(verbose_name='库存')),
                ('image', models.ImageField(verbose_name='图片', upload_to='apps')),
                ('desc', models.CharField(verbose_name='商品简述', max_length=256)),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
                'db_table': 'df_cake_sku',
            },
        ),
        migrations.CreateModel(
            name='Cake_Spu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('detele_time', models.BooleanField(verbose_name='删除标记', default=True)),
                ('name', models.CharField(verbose_name='商品spu名称', max_length=20)),
                ('detail', tinymce.models.HTMLField(verbose_name='商品详情', blank=True)),
            ],
            options={
                'verbose_name': '商品Spu',
                'verbose_name_plural': '商品Spu',
                'db_table': 'df_cake_spu',
            },
        ),
        migrations.CreateModel(
            name='CakeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('detele_time', models.BooleanField(verbose_name='删除标记', default=True)),
                ('name', models.CharField(verbose_name='商品种类名称', max_length=10)),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_cake_type',
            },
        ),
        migrations.AddField(
            model_name='cake_sku',
            name='cake_spu',
            field=models.ForeignKey(verbose_name='商品Spu', to='cake.Cake_Spu'),
        ),
        migrations.AddField(
            model_name='cake_sku',
            name='type',
            field=models.ForeignKey(verbose_name='商品种类', to='cake.CakeType'),
        ),
    ]
