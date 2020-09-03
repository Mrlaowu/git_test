from django.shortcuts import render
from django.views.generic import View
from tool.mixin import LoginRequeredMixin
from django.http import JsonResponse
from redis import StrictRedis
from cake.models import Cake_Sku

#ajax post param:  cake_id、count、total_price
class CartAddView(LoginRequeredMixin,View):
    def post(self,request):
        user=request.user
        #获取参数
        cake_id=request.POST.get("cake_id")
        count=request.POST.get("count")
        total_price=request.POST.get("total_price")

        #效验参数
        if not all([cake_id,count,total_price]):
            return JsonResponse({"res":1,"errmsg":"参数不完整"})

        #效验添加的商品
        try:
            count=int(count)
        except Exception as e:
            return JsonResponse({"res":2,"errmsg":"商品数量异常"})

        try:
            cake=Cake_Sku.objects.get(id=cake_id)
        except Exception as e:
            return JsonResponse({"res":3,"errmsg":"商品不存在"})


        #业务逻辑处理：添加数据到redis中 hash  key:cart_user.id   value:(cake_id:count)
        conn=StrictRedis()
        #拼接hash的key
        cart_key="cart_%d"%user.id

        #先获取购物车中的商品数目
        cart_count=conn.hget(cart_key,cake_id)
        if cart_count:
            #累加购物车中商品的数目
            count+=int(cart_count)

        #效验商品的库存
        if count > cake.stock:
            return JsonResponse({"res":4,"errmsg":"商品库存不足"})

        #设置hash中cake_id的值
        #hash -> 如果cake_id已存在，更新数据，如果cake_id不存在,添加数据
        conn.hset(cart_key,cake_id,count)

        #计算用户购物车商品的条目数
        total_count=conn.hlen(cart_key)

        #返回响应
        return JsonResponse({"res":0,"total_count":total_count})

#redis购物车信息  hash cart_id  cake_id:count
class CartInfoView(LoginRequeredMixin,View):
    """购物车主页"""
    def get(self,request):
        user=request.user
        #获取用户购物车中商品的信息
        conn=StrictRedis()
        cart_key="cart_%d"%user.id
        #{"商品id":'商品数量'}
        cart_dict=conn.hgetall(cart_key)

        skus=[]
        #保存用户购物车中商品的总数目和总价格
        total_count=0
        total_price=0
        #遍历获取商品的信息
        for cake_id,count in cart_dict.items():
            #根据商品的id 获取商品的信息
            cake=Cake_Sku.objects.get(id=cake_id)
            #计算商品的小计
            amount=cake.price*int(count)
            #动态给cake对象增加一个属性amount,保存商品的小计
            cake.amount=amount
            #动态给cake对象增加一个属性count,保存购物车中对应商品的数量
            cake.count=count

            skus.append(cake)
            #累加计算商品的总数目和总价格
            total_count+=int(count)
            total_price+=amount

        #组织上下文
        context={
            "total_count":total_count,
            "total_price":total_price,
            "skus":skus
        }
        return render(request,'cart.html',context)

#http:127.0.0.1:8000/cart/delete
class CartDelView(LoginRequeredMixin,View):
    def post(self,request):
        """删除购物车操作
        param:cake_id"""
        user=request.user
        #接受参数
        cake_id=request.POST.get("cake_id")
        #效验参数
        if not cake_id:
            return JsonResponse({"res":1,"errmsg":"cake_id参数为空"})

        try:
            cake=Cake_Sku.objects.get(id=cake_id)
        except Exception as e:
            return JsonResponse({"res":2,"errmsg":"该cake不存在"})

        #业务逻辑处理 : 删除redis中id=cake_id的数据
        conn=StrictRedis()
        cart_key="cart_%d"%user.id

        conn.hdel(cart_key,cake_id)

        #返回响应
        return JsonResponse({"res":0})