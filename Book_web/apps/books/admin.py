from django.contrib import admin
from .models import Books,BooksType
from django.core.cache import cache
# Register your models here.

class BaseAdmin(admin.ModelAdmin):
    """模型管理基类"""
    def save_model(self, request, obj, form, change):
        """新增或更新表中的数据时调用"""
        super().save_model(request,obj,form,change)
        #发出任务,让celery worker重新生成首页静态页　　--异步
        from celery_task.tasks import generate_static_index_html
        generate_static_index_html.delay()

        #清除首页的缓存数据
        cache.delete("index_page_data")

    def delete_model(self, request, obj):
        """删除表中的数据时调用"""
        super().delete_model(request,obj)
        #发出任务,让celery worker重新生成首页静态页　　
        from celery_task.tasks import generate_static_index_html
        generate_static_index_html.delay()

        #清除首页的缓存数据
        cache.delete("index_page_data")

class BooksAdmin(BaseAdmin):
    """Book模型管理"""
    list_display = ['title','author']

class BooksTypeAdmin(BaseAdmin):
    """Book分类模型类"""
    list_display = ['name']

admin.site.register(Books,BooksAdmin)
admin.site.register(BooksType,BooksTypeAdmin)