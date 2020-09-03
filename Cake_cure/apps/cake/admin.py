from django.contrib import admin
from .models import Cake_Sku,Cake_Spu,CakeType
from django.core.cache import cache

class BaseAdmin(admin.ModelAdmin):
    """模型管理基类"""
    def save_model(self, request, obj, form, change):
        """新增或更新表中的数据是调用"""
        super().save_model(request,obj,form,change)
        #发送任务,让celery worker 重新生成首页静态页　
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        cache.delete("index_page_data")

    def delete_model(self, request, obj):
        super().delete_model(request,obj)
        #发送任务
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()
        cache.delete("index_page_data")


class CakeSkuAdmin(BaseAdmin):
    """cake_sku模型管理类"""
    list_display = ["name","type"]

class CakeSpuAdmin(BaseAdmin):
    """cake_sku模型管理类"""
    list_display = ["name"]

class CakeTypeAdmin(BaseAdmin):
    """cake_sku模型管理类"""
    list_display = ["name"]

#注册模型管理类
admin.site.register(Cake_Sku,CakeSkuAdmin)
admin.site.register(Cake_Spu,CakeSpuAdmin)
admin.site.register(CakeType,CakeTypeAdmin)