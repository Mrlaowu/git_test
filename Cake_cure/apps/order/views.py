from django.shortcuts import render,HttpResponse
from tool.mixin import LoginRequeredMixin
from django.views.generic import View
from redis import StrictRedis
from cake.models import Cake_Sku
from user.models import Address
import random
from datetime import datetime
import time
from django.http import JsonResponse
from django.db import transaction
from .models import Orderinfo,OrderCake

#http:127.0.0.1:8000/order/commit
class OrderCommit(View):
    def get(self,request):
        """提交订单页
        parmas:{cake_id:count}"""

        user=request.user
        conn=StrictRedis()
        #获取购物车记录
        cart_key="cart_%d"%user.id

        #{'cake_id':'count'}
        cart_dict=conn.hgetall(cart_key)

        #address
        addr=Address.objects.get_default_address(user)
        if not addr:
            return  HttpResponse("addr not exit")

        cakes=[]
        total_price=0
        total_count=0

        #遍历
        for cake_id,count in cart_dict.items():
            cake=Cake_Sku.objects.get(id=cake_id)
            #xiao ji
            amount=cake.price*int(count)
            #cake add attr
            cake.amount=amount
            cake.count=count

            cakes.append(cake)

            #zongjia  zong  shumu
            total_price+=amount
            total_count+=int(count)

        context={
            "total_price":total_price,
            "total_count":total_count,
            "cakes":cakes,
            "addr":addr
        }

        return render(request,"place_order.html",context)

#http:127.0.0.1:8000:/order/create  post ajax  乐观锁
class CreateOrderView(LoginRequeredMixin,View):
    def post(self,request):
        """user order page
        param {cake_ids,count,amount,order_id,addr_id}"""
        #get data

        user=request.user
        addr_id=request.POST.get("addr_id")
        try:
            addr=Address.objects.get(id=addr_id)
        except Exception as e:
            return JsonResponse({"res":2,"errmsg":"addr is error"})

        #check data
        if not all([addr_id]):
            return JsonResponse({"res":1,"errmsg":"data not all"})

        #redis cart_history
        conn=StrictRedis()
        cart_key="cart_%d"%user.id

        #cake_ids
        cake_ids=conn.hkeys(cart_key)
        cake_ids=[int(cake) for cake in cake_ids]

        # todo: create order
        # organize param
        #order_id 2020xxxx+user.id
        order_id=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+str(user.id)
        #transit_price
        transit_price=0

        #total_price total_count
        total_count=0
        total_price=0

        #set savepoint
        save_id=transaction.savepoint()
        try:
            try:
                # todo: df_order_info
                order=Orderinfo.objects.create(order_id=order_id,
                                               user=user,
                                               addr=addr,
                                               total_count=total_count,
                                               total_price=total_price,
                                               transit_price=transit_price)
            except Exception as e:
                print(e)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({"res":6,"errmsg":"create order fail"})

            # todo: create df_order_goods
            for cake_id in cake_ids:
                for i in range(3):
                    try:

                        # select *from df_cake_sku where id=cake_id for update;
                        # cake=Cake_Sku.objects.select_for_update().get(id=cake_id)
                        cake = Cake_Sku.objects.get(id=cake_id)
                    except:
                        # cake not exit
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({"res": 3, "errmsg": "cake is null"})

                        # redis get cake'count
                    count = conn.hget(cart_key, cake_id)
                    # todo: cake.stock
                    if int(count) > cake.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({"res": 4, "errmsg": "count > stock"})

                    # todo:更新上您的库存
                    origin_stock = cake.stock
                    new_stock = origin_stock - int(count)
                    #
                    # print("user:%d stock:%d" % (user.id, cake.stock))
                    # import time
                    # time.sleep(5)

                    # update df_gooods_sku set stock=new_stock ,sales=new_sales
                    # where id=sku_id and stock =origin_stock
                    # 返回受影响的行数　　-- 乐观锁   update shi panduan
                    res = Cake_Sku.objects.filter(id=cake_id, stock=origin_stock).update(stock=new_stock)
                    if res == 0:
                        if i==2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({"res": 7, "errmsg": "下单失败--2"})
                        continue

                    # todo:向df_order_goods表中添加一条记录
                    OrderCake.objects.create(order=order,
                                             sku=cake,
                                             count=count,
                                             price=cake.price)

                    # todo:更新上您的total_count和total_price
                    amount = cake.price * int(count)
                    total_price += amount
                    total_count += int(count)

                    break

            # todo:更新订单信息表中的商品的总数量和总价格
            order.total_count=total_count
            order.total_price=total_price
            order.save()

        except Exception as e:
            print(e)
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res':5,'errmsg':'order fail'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # todo:清除用户购物车中对应的记录  *对列表拆包　[1,3]->1,3
        conn.hdel(cart_key,*cake_ids)

        return JsonResponse({"res":0})

#http:127.0.0.1:8000:/order/create  post ajax
#class CreateOrderView(LoginRequeredMixin,View):
#     def post(self,request):
#         """user order page
#         param {cake_ids,count,amount,order_id,addr_id}"""
#         #get data
#
#         user=request.user
#         addr_id=request.POST.get("addr_id")
#         try:
#             addr=Address.objects.get(id=addr_id)
#         except Exception as e:
#             return JsonResponse({"res":2,"errmsg":"addr is error"})
#
#         #check data
#         if not all([addr_id]):
#             return JsonResponse({"res":1,"errmsg":"data not all"})
#
#         #redis cart_history
#         conn=StrictRedis()
#         cart_key="cart_%d"%user.id
#
#         #cake_ids
#         cake_ids=conn.hkeys(cart_key)
#         cake_ids=[int(cake) for cake in cake_ids]
#
#         # todo: create order
#         # organize param
#         #order_id 2020xxxx+user.id
#         order_id=datetime.now().strftime("%Y%m%d%H%M%S")+'_'+str(user.id)
#         #transit_price
#         transit_price=0
#
#         #total_price total_count
#         total_count=0
#         total_price=0
#
#         #set savepoint
#         save_id=transaction.savepoint()
#         try:
#             try:
#                 # todo: df_order_info
#                 order=Orderinfo.objects.create(order_id=order_id,
#                                                user=user,
#                                                addr=addr,
#                                                total_count=total_count,
#                                                total_price=total_price,
#                                                transit_price=transit_price)
#             except Exception as e:
#                 print(e)
#                 transaction.savepoint_rollback(save_id)
#                 return JsonResponse({"res":6,"errmsg":"create order fail"})
#
#             # todo: create df_order_goods
#             for cake_id in cake_ids:
#                 try:
#                     #查询时加锁---悲观锁
#                     #select *from df_cake_sku where id=cake_id for update;
#                     # cake=Cake_Sku.objects.select_for_update().get(id=cake_id)
#                     # cake=Cake_Sku.objects.get(id=cake_id)
#                     cake= Cake_Sku.objects.select_for_update().get(id=cake_id)
#                 except:
#                     #cake not exit
#                     transaction.savepoint_rollback(save_id)
#                     return JsonResponse({"res":3,"errmsg":"cake is null"})
#
#                 print("user:%d stock:%d"%(user.id,cake.stock))
#                 import time
#                 time.sleep(5)
#
#                 #redis get cake'count
#                 count=conn.hget(cart_key,cake_id)
#                 #todo: cake.stock
#                 if int(count)>cake.stock:
#                     transaction.savepoint_rollback(save_id)
#                     return JsonResponse({"res":4,"errmsg":"count > stock"})
#
#                 # todo:向df_order_goods表中添加一条记录
#                 OrderCake.objects.create(order=order,
#                                          sku=cake,
#                                          count=count,
#                                          price=cake.price)
#                 # todo:更新上您的库存
#                 cake.stock-=int(count)
#                 cake.save()
#
#                 # todo:更新上您的total_count和total_price
#                 amount=cake.price*int(count)
#                 total_price+=amount
#                 total_count+=int(count)
#
#             # todo:更新订单信息表中的商品的总数量和总价格
#             order.total_count=total_count
#             order.total_price=total_price
#             order.save()
#
#         except Exception as e:
#             print(e)
#             transaction.savepoint_rollback(save_id)
#             return JsonResponse({'res':5,'errmsg':'order fail'})
#
#         # todo:清除用户购物车中对应的记录  *对列表拆包　[1,3]->1,3
#         conn.hdel(cart_key,*cake_ids)
#
#         return JsonResponse({"res":0})




