from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.cache import cache
from .models import Books,BooksType
from utils.mixin import LoginRequeredMixin
from django.core.urlresolvers import reverse
from redis import StrictRedis
from django.core.paginator import Paginator


#http://……books/index
class IndexView(View):
    """主页"""
    def get(self,request):
        #验证用户是否登录
        user=request.user
        if not user.is_authenticated():
            return redirect(reverse("user/login"))

        #读取缓存
        context=cache.get("index_page_data")

        if context is None:
            #获取书籍数据
            books = Books.objects.all()
            #获取所有的书籍种类
            types = BooksType.objects.all()
            #组织上下文
            context={
                "books":books,
                "types":types,
            }
            #设置缓存
            cache.set("index_page_data",context,3600)
        return render(request,'static_index.html',context)


#http:127.0.0.1:8000/books/detail/{book_id}
class DetailView(LoginRequeredMixin,View):
    """详情页"""
    def get(self,request,bid):
        user=request.user
        try:
            book=Books.objects.get(id=bid)
        except Exception as e:
            return render(request,'detail.html',{"errmsg":'查询数据库错误'})

        #---------访问详情页-将历史浏览记录添加到redis中
        conn=StrictRedis()
        history_key="history_%d"%user.id
        #移除列表中的book_id
        conn.lrem(history_key,0,bid)
        #把book_id插入到列表的左侧
        conn.lpush(history_key,bid)
        #只保存用户最新浏览的三条　　－lrange
        conn.ltrim(history_key,0,2)

        #组织上下文
        context={
            'book':book
        }
        return render(request,"detail.html",context)

#/books/list/{type_id}/page
class ListView(LoginRequeredMixin,View):
    """列表页"""
    def get(self,request,btype_id,page):
        #根据书籍种类－－查询多类的书籍　　一查多
        try:
            b_type = BooksType.objects.get(id=btype_id)
            books = b_type.books_set.all()

        except Exception as e:
            return render(request,'list.html',{'errmsg':'查询数据库错误'})

        #对商品进行分页
        paginator=Paginator(books,1)

        try:
            page=int(page)
        except Exception as e:
            page=1
        if page>paginator.num_pages :
            page=1

        # 获取第page页的内容
        skus_page=paginator.page(page)

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
            'books':books,
            "pages":pages,
            "skus_page":skus_page,
            "type_id":btype_id
        }

        return render(request,'list.html',context)






