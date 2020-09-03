from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
import re
from .models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from celery_tasks.tasks import send_register_active_email
from tool.mixin import LoginRequeredMixin
from redis import StrictRedis
from cake.models import Cake_Sku
from .models import Address
import random
from datetime import datetime
import time
from django.http import JsonResponse
from django.db import transaction
from order.models import Orderinfo,OrderCake
from django.core.paginator import Paginator

class RegisterView(View):
    """注册"""
    def get(self,request):
        """显示注册页面"""
        return render(request,"register.html")

    def post(self,request):
        """进行注册处理
        :param:user_name email password password2"""
        #接受数据
        username=request.POST.get("username")
        email=request.POST.get("email")
        password=request.POST.get("password")
        password2=request.POST.get("password2")

        #效验数据
        if not all([username,email,password2,password]):
            return render(request,"register.html",{"errmsg":"数据不完整"})

        #验证邮箱格式  xiaowu@qq.com.cn
        if not re.match(r"^\w+@\w+(\.\w+){1,2}$",email):
            return render(request,"register.html",{"errmsg":"邮箱格式错误"})

        #前后密码不一致
        if password != password2:
            return render(request,"register.html",{"errmsg":'前后密码不一致'})

        #用户是否已存在
        try:
            user=User.objects.filter(username=username)
        except Exception as e:
            user=None

        if user:
            return render(request,"register.html",{"errmsg":"用户已存在"})

        #业务逻辑处理：添加用户信息,使用django默认认证系统保存用户数据到数据库中
        user=User.objects.create_user(username,email,password)
        user.is_active=0
        user.save()

        #发送激活邮件,包含激活链接:https://127.0.0.1:8000/user/active/3
        #激活链接需要包含用户的身份信息　--加密

        #加密用户的身份信息，生成激活token--Serializer
        serializer=Serializer(settings.SECRET_KEY,3600)
        info={"confirm":user.id}
        token=serializer.dumps(info)
        #加密的数据是byes类型,对其进行解码
        token=token.decode()

        #发送邮件--发送任务到任务队列  delay
        send_register_active_email.delay(email,username,token)

        #返回响应
        return redirect(reverse("user:login"))


class ActiveView(View):
    """激活用户"""
    def get(self,request,token):
        #创建Serializer对象,获取秘钥,进行解密,获取要激活的用户信息
        serializer=Serializer(settings.SECRET_KEY,3600)
        try:
            #获取解密的数据
            info=serializer.loads(token)
            #获取待激活用户的id
            user_id=info["confirm"]
            #根据id获取用户信息
            user=User.objects.get(id=user_id)
            user.is_active=1
            user.save()

            #跳转到登录页面
            return redirect(reverse("user:login"))
        except Exception as e:
            #激活链接已过期
            return HttpResponse("激活链接过期")


class LoginView(View):
    """登录用户"""
    def get(self,request):
        return render(request,"login.html")

    def post(self,request):
        """
        param:username password
        :param request:
        :return:
        """
        #接受参数
        username=request.POST.get("username")
        password=request.POST.get("password")

        #效验参数
        if not all([username,password]):
            return render(request,"login.html",{"errmsg":"参数不完整"})

        #判断用户是否存在
        user=authenticate(username=username,password=password)
        if user is not None:
            #用户名密码正确： 业务逻辑处理　判断是否激活
            if user.is_active:
                #用户名激活
                #记录用户的登录状态　--session
                login(request,user)

                #跳转到首页
                return redirect(reverse("cake:index"))

            else:
                #用户未激活
                return  render(request,"login.html",{"errmsg":"用户未激活"})
        else:
            return render(request,"login.html",{"errmsg":"用户名或密码错误"})

#http://127.0.0.1:8000/user/info
class UserinfoView(LoginRequeredMixin,View):
    def get(self,request):
        """用户中心页"""
        user=request.user

        sr=StrictRedis()

        history_key="history_%d"%user.id

        #获取用户最近浏览的4个商品
        cake_ids=sr.lrange(history_key,0,3)

        cakes=[]
        #遍历获取用户浏览的商品信息
        for id in cake_ids:
            #获取浏览的商品
            cake=Cake_Sku.objects.get(id=id)
            cakes.append(cake)

        #组织参数
        context={
            "user":user,
            "cakes":cakes
        }

        return render(request,"user_info.html",context)


#http://127.0.0.1:8000/user/addr  post
class UserAddrView(LoginRequeredMixin,View):
    def get(self,request):
        user=request.user

        #获取用户的默认收货地址
        address=Address.objects.get_default_address(user)

        return render(request,"user_addr.html",{"address":address})

    def post(self,request):
        """用户地址页
        param:receiver、addr、phone、zip_code"""

        #获取参数
        receiver=request.POST.get("receiver")
        zip_code=request.POST.get("zip_code")
        phone=request.POST.get("phone")
        addr=request.POST.get("addr")

        #效验参数
        if not all([receiver,zip_code,phone,addr]):
            return render (request,"user_addr.html",{"errmsg":"参数不完整"})

        if not re.match(r"1[34578]\d{9}",phone):
            return render(request,"user_addr.html",{"errmsg":"手机号格式不对"})

        #业务逻辑处理：添加地址
        #如果用户已存在默认收货地址,添加的地址不作为默认收货地址，否则作为默认收货地址

        user=request.user

        #判断是否有默认地址
        address=Address.objects.get_default_address(user)

        if address:
            is_default=False
        else:
            is_default=True

        #添加地址
        try:
            Address.objects.create(user=user,receiver=receiver,
                addr=addr,zip_code=zip_code,phone=phone,
                is_default=is_default)
        except Exception as e:
            return render(request,"user_addr.html",{"errmsg":"Address添加失败"})
        #返回响应
        return redirect((reverse("user:addr")))



# #http:127.0.0.1:8000:/user/order
class UserOrderView(LoginRequeredMixin,View):
    def get(self,request,page):
        """user order page
        param {cakes,count,amount,order_id,addr_id}"""

        user=request.user

        #orders
        orders=Orderinfo.objects.all()

        for order in orders:
            order_cakes=OrderCake.objects.filter(order=order)

            for order_cake in order_cakes:
                #amount
                amount=order_cake.price*order_cake.count
                #动态给order_sku增加属性amount，保存订单商品的小计
                order_cake.amount=amount

            #动态给order增加属性，保存订单状态标题
            order.status_name=Orderinfo.ORDER_STATUS[order.order_status]
            #动态给order增加属性,保存订单商品的信息
            order.order_cakes=order_cakes

        #pagenator
        paginator=Paginator(orders,1)

        try:
            page=int(page)
        except Exception as e:
            page=1
        if page>paginator.num_pages:
            page=1

        # 获取第page页的内容
        order_page=paginator.page(page)

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
            "order_page":order_page,
            "pages":pages
        }

        return render(request,"user_order.html",context)