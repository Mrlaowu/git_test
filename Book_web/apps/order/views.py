from django.shortcuts import render,redirect
from django.views.generic import View
from django.core.cache import cache
from apps.books.models import Books,BooksType
from utils.mixin import LoginRequeredMixin
from django.core.urlresolvers import reverse
from redis import StrictRedis
from django.http import JsonResponse
from alipay import AliPay
import os
from django.conf import settings
from datetime import datetime

#http:127.0.0.1:8000/order/{book_id}
class OrderView(LoginRequeredMixin,View):
    """订单页"""
    def get(self,request,book_id):
        #查询数据库
        try:
            book=Books.objects.get(id=book_id)
        except Exception as e:
            return render(request,'order.html',{'errmsg':'数据库查询失败'})
        #组织上下文
        context={
            'book':book
        }

        return render(request,"order.html",context)


#http:127.0.0.1:8000:/order/pay
#传递参数：count、amount、book_id--ajax、post
class OrderPayView(LoginRequeredMixin,View):
    def post(self,request):
        """订单支付"""
        #获取参数
        count=request.POST.get("count")
        amount=request.POST.get("amount")
        book_id=request.POST.get("book_id")
        user=request.user

        #效验参数
        if not all([count,amount,book_id]):
            return JsonResponse({"res":1,'errmsg':"参数不完整"})

        try:
            book=Books.objects.get(id=book_id)
        except Exception as e:
            return JsonResponse({'res':2,'errmsg':'数据库查询失败'})

        if book.count < int(count):
            return JsonResponse({'res':3,'errmsg':'商品库存不足'})

        #业务逻辑处理
        #支付宝沙箱初始化
        try:
            alipay = AliPay(
                appid="2016102200735359",  # 应用的id
                app_notify_url=None,  # 默认回调url
                app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
                # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
                sign_type="RSA2",  # RSA 或者 RSA2
                debug=True # 默认False
            )
        except Exception as e:
            return JsonResponse({'res':5,'errmsg':'支付宝沙箱引入失败！'})

        #调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string

        order_id = datetime.now().strftime("%Y%m%d%H%M%S") + '_' + str(user.id)
        total_pay = float(amount)  # Decimal
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),  # 支付总金额
            subject='三维书店%s'%order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )

        #返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?'+ order_string
        return JsonResponse({'res':0,'pay_url':pay_url,'order_id':order_id})

# ajax post
# params: order_id、book_id、count
# /order/check
class CheckPayView(View):
    """查看订单支付的结果"""
    def post(self,request):
        """查看支付结果"""
        #用户是否登录
        user=request.user
        if not user.is_authenticated():
            return JsonResponse({'res':1,"errmsg":"用户未登录"})

        #接收参数
        order_id=request.POST.get("order_id")
        book_id=request.POST.get("book_id")
        count=request.POST.get("count")

        #效验参数
        if not all([order_id,book_id,count]):
            return JsonResponse({'res':2,'errmsg':'无效的订单'})

        try:
            book=Books.objects.get(id=book_id)
        except Exception as e:
            return JsonResponse({'res':3,'errmsg':'数据库查询失败'})

        #业务逻辑处理：使用Python sdk调用支付宝的支付接口
        alipay = AliPay(
            appid="2016102200735359",  # 应用的id
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        #调用支付宝的交易查询接口
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get('code')

            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                #支付成功
                #获取支付宝交易号
                trade_no=response.get('trade_no')
                #更新数据库的库存
                count=int(count)
                book.count-=count
                book.save()
                #返回结果
                return JsonResponse({'res':0,'message':'支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                #等待买家付款
                #业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                #支付出错  -打印状态码
                print(code)
                return JsonResponse({'res':4,'errmsg':'支付失败'})



