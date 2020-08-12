# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=True)),
                ('title', models.CharField(verbose_name='书籍标题', max_length=20)),
                ('price', models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2)),
                ('image', models.ImageField(verbose_name='书籍图片', upload_to='books')),
                ('count', models.IntegerField(verbose_name='书籍数量', default=1)),
                ('detail', tinymce.models.HTMLField(verbose_name='书籍详情', blank=True)),
                ('author', models.CharField(verbose_name='作者', max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BooksType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('is_delete', models.BooleanField(verbose_name='删除标记', default=True)),
                ('name', models.CharField(verbose_name='种类名称', max_length=20)),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_books_type',
            },
        ),
        migrations.AddField(
            model_name='books',
            name='type',
            field=models.ForeignKey(verbose_name='书籍种类', to='books.BooksType'),
        ),
    ]
