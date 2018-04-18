# coding=utf-8
from datetime import datetime
from django.db import transaction
from django.shortcuts import render, redirect
from df_user import user_decorator
from df_user.models import *
from df_cart.models import *
from models import *


@user_decorator.login
def order(request):
    # 查询用户对象
    user = UserInfo.objects.get(id=request.session['user_id'])
    # 根据提交查询购物车信息
    get = request.GET
    # 获取多选框的值
    cart_ids = get.getlist('cart_id')
    cart_ids1 = [int(item) for item in cart_ids]
    carts = CartInfo.objects.filter(id__in=cart_ids1)
    # 构造传递到模板中的数据
    context = {
        'title': '提交订单', 'page_name': 1,
        'carts': carts, 'user': user,
        'cart_ids': ','.join(cart_ids)
    }
    return render(request, 'df_order/place_order.html', context)


'''
事务：一旦操作失败则全部回退
1、创建订单对象
2、判断商品的库存
3、创建详单对象
4、修改商品库存
5、删除购物车
'''


@transaction.atomic()
@user_decorator.login
def order_handle(request):
    # 记录事务的开启点
    trans_id = transaction.savepoint()
    # 获取cart_ids,购物车编号
    cart_ids = request.POST.get('cart_ids')
    print('-----123-----')
    try:
        order = OrderInfo()
        # 当前日期
        now = datetime.now()
        # 用户ｉｄ
        uid = request.session['user_id']
        # 订单id
        order.oid = '%s%d' % (now.strftime('%Y%m%d%H%M%S'), uid)
        order.user_id = uid
        # 订单日期
        order.odate = now
        # 订单地址
        order.oaddress = request.POST.get('address')
        # 订单总额
        order.ototal = 0
        # 保存订单
        order.save()
        print('-----321----')
        # 创建详单对象，分割成数组
        cart_ids1 = [int(item) for item in cart_ids.split(',')]
        total = 0  # 记录总额
        for id1 in cart_ids1:
            detail = OrderDetailInfo()
            detail.order = order
            # 查询购物车信息
            cart = CartInfo.objects.get(id=id1)
            # 判断商品库存
            goods = cart.goods
            if goods.gkucun >= cart.count:  # 如果库存大于购买数量
                # 减少商品库存
                goods.gkucun = cart.goods.gkucun - cart.count
                goods.save()
                # 完善详单信息
                # detail.goods_id = goods.id
                detail.goods = goods
                price = goods.gprice
                detail.price = price
                count = cart.count
                detail.count = count
                detail.save()
                total = total + price * count
                # 删除购物车数据
                cart.delete()
            else:  # 如果库存小于购买数量
                transaction.savepoint_rollback(trans_id)
                return redirect('/cart/')
        # 保存总价
        order.ototal = total + 10
        order.save()
        transaction.savepoint_commit(trans_id)
    except Exception as e:
        print '================%s' % e
        transaction.savepoint_rollback(trans_id)

    return redirect('/user/order/')


def pay(request, pid):
    order = OrderInfo.objects.get(oid=pid)
    order.oIsPay = True
    order.save()
    context = {'order': order}
    return render(request, 'df_order/pay.html', context)

