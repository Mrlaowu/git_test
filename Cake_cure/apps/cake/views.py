from django.shortcuts import render
from django.views.generic import View
from tool.mixin import LoginRequeredMixin
from django.http import HttpResponse
from .models import Cake_Spu,CakeType,Cake_Sku
from django.core.cache import cache
from redis import StrictRedis
from django.core.paginator import Paginator

class IndexView(LoginRequeredMixin,View):
    """首页"""
    def get(self,request):
        #读取缓存
        context=cache.get("index_page_data")

        if context is None:
            print("---------这是缓存----------")

            #查询数据库
            try:
                types=CakeType.objects.all()
            except Exception as e:
                return render(request,"static_index.html",{"errmsg":"CakeType查询错误"})

            try:
                cakes=Cake_Sku.objects.all()
            except Exception as e:
                return render(request,"static_index.html",{"errmsg":"Cake_Spu查询错误"})

            #组织参数
            context={
                "cakes":cakes,
                "types":types
            }

            #设置缓存
            cache.set("index_page_data",context,3600)

        #查询成功，返回响应
        return render(request,"static_index.html",context)

#127.0.0.1:8000/list/type_id=xxx?page=yyy
class ListView(LoginRequeredMixin,View):
    def get(self,request,type_id,page):
        """列表页
        param:type_id"""

        #效验参数是否存在
        try:
            type=CakeType.objects.get(id=type_id)
        except Exception as e:
            return render(request,"list.html",{"errmsg":"caketype查询失败"})

        #业务逻辑处理
        try:
            cakes=Cake_Sku.objects.filter(type=type_id)
        except Exception as e:
            return render(request,"list.html",{"errmsg":"cakesku查询失败"})

        #对商品进行分页
        paginator=Paginator(cakes,2)

        try:
            page=int(page)
        except Exception as e:
            page=1
        if page>paginator.num_pages:
            page=1

        #获取地page页的内容
        cakes_page=paginator.page(page)
        print(cakes_page.object_list)

        # todo: 进行页码的控制，页面上最多显示５个页码
        #1.总页数小于五页，页面上显示所有页码
        #2.如果当前是前３页，显示１－５页
        #3.如果当前是后３页，显示后５页
        #4.其他情况,显示当前页的前２页，当前页，当前页的后２页
        num_pages=paginator.num_pages
        if num_pages<5:
            pages=range(1,num_pages+1)
        elif page<3:
            pages=range(1,6)
        elif num_pages-page<=2:
            pages=range(num_pages-4,num_pages+1)
        else :
            pages=range(page-2,page+3)

        context={
            "cakes_page":cakes_page,
            "pages":pages,
            "type":type
        }

        return render(request,"list.html",context)

#127.0.0.1:8000/detail/cake_id=xxx
class DetailView(LoginRequeredMixin,View):
    def get(self,request,cake_id):
        """详情页
        param:cake_id"""
        user=request.user

        #效验参数是否存在
        try:
            cake=Cake_Sku.objects.filter(id=cake_id)
        except Exception as e:
            return render(request,"list.html",{"errmsg":"cakesku查询失败"})

        #redis中添加历史浏览记录  --list
        sr=StrictRedis()
        history_key="history_%d"%user.id

        #删除list中包含的记录
        sr.lrem(history_key,0,cake_id)

        #lpush添加历史记录
        sr.lpush(history_key,cake_id)

        #只显示3条历史记录
        sr.ltrim(history_key,0,2)


        #组织参数
        context={
            "cakes":cake
        }

        return render(request,"detail.html",context)



