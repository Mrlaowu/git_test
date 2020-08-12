from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.conf import settings
from .models import User
import re
from celery_task.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.contrib.auth import authenticate,login,logout
from redis import StrictRedis
from apps.books.models import BooksType,Books

class RegisterView(View):
    def get(self,request):
        return render(request,"register.html")

    def post(self,request):
        """注册"""
        #1.接受参数
        username=request.POST.get("username")
        password=request.POST.get("password")
        password2=request.POST.get("password2")
        email=request.POST.get("email")

        #2.效验参数
        if not all([username,password,password2,email]):
            return render(request,"register.html",{'errmsg':"数据不完整"})

        #邮箱效验
        if re.match(r'^[0-9a-z]*@[\w]\.[\w]{3,4}$',email):
            return render(request,'register.html',{'errmsg':"邮箱错误"})

        #密码必须为６-12位
        if not re.match(r'^[\w]{6,12}',password):
            return render(request,'register.html',{'errmsg':'密码长度错误'})

        #两次密码不重复
        if password != password2:
            return render(request,'register.html',{'errmsg':'两次密码不一致'})

        #3.业务逻辑处理：对用户进行注册

        #效验用户是否注册
        try:
            user=User.objects.get(username=username)
        except User.DoesNotExist:
            #或户名不存在
            user=None

        if user:
            #用户名已经注册
            return render(request,'register.html',{'errmsg':'用户名已经注册'})

        #使用django默认认证系统保存用户数据到数据库
        user=User.objects.create_user(username,email,password)
        user.is_active=0
        user.save()

        #发送激活邮件，包含激活链接：https://127.0.0.1:8001/user/active/3
        #激活链接中需要包含用户的身份信息－加密

        #加密用户的身份信息，生成激活的token
        serializer=Serializer(settings.SECRET_KEY,3600)
        info={'confirm':user.id}
        token=serializer.dumps(info)
        #加密的数据是byes类型，对其进行解密
        token=token.decode()

        # 发邮件---发送任务到任务队列　　delay
        send_register_active_email.delay(email, username, token)

        #4.返回响应
        return render(request,'login.html')


class ActiveView(View):
    """用户激活"""
    def get(self,request,token):
        """进行用户激活"""
        #创建Serailizer对象，获取秘钥，进行解密，获取要激活的用户信息
        print("haha")
        serializer=Serializer(settings.SECRET_KEY,3600)
        try:
            #获取解密的数据
            info=serializer.loads(token)
            #获取待激活用户的id
            user_id=info['confirm']
            #根据id获取用户信息
            user=User.objects.get(id=user_id)
            user.is_active=1
            user.save()

            #跳转到登录页面
            # return redirect(reverse("user:login"))
            return HttpResponse("激活success,您可以登录了")

        except Exception as e:
            #激活链接已过期
            return HttpResponse("激活链接过期")

class LoginView(View):
    """用户登录"""
    def get(self,request):
        return render(request,'login.html')

    def post(self,request):
        #1.获取参数
        username=request.POST.get('username')
        password=request.POST.get("password")

        #2.效验参数
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'参数不完整'})

        #3.业务逻辑处理： 登录效验
        user=authenticate(username=username,password=password)
        if user is not None:
            #用户名密码正确
            if user.is_active:
                #获取名激活
                #记住用户的登录状态－－session
                login(request,user)

                #记录状态后跳转到books:index页面
                return redirect(reverse('books:index'))

            else:
                return render(request,'login.html',{'errmsg':'用户未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户名或者密码错误'})


class LogoutView(View):
    """退出视图"""
    def get(self,request):
        #清除所有的session
        logout(request)

        return redirect(reverse("user:login"))

class ProfileView(View):
    """用户中心"""
    def get(self,request):
        #获取用户的个人信息
        user=request.user

        #获取用户的浏览记录
        sr=StrictRedis()
        #拼接特定用户名
        history_key="history_%d"%user.id

        #获取用户最新浏览的５个商品id
        book_ids=sr.lrange(history_key,0,4)

        #遍历获取用户浏览的商品信息
        books_li=[]
        for id in book_ids:
            #获取浏览的商品
            book=Books.objects.get(id=id)
            books_li.append(book)

        #组织上下文
        context={
            "books":books_li
        }

        return render(request,'profile.html',context)



