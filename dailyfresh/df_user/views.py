# coding=utf-8
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect
from models import *
from hashlib import sha1


def register(request):
    return render(request, 'df_user/register.html')


def register_handle(request):
    # 接收用户输入的值
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两次密码
    if upwd != upwd2:
        return redirect('/user/register/')
    # 密码加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()
    # 创建对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    # 注册成功，转到登录页
    return redirect('/user/login/')


def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({"count": count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {"title": "用户登录", "error_name": 0, "error_pwd": 0, "uname": uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查找对象
    users = UserInfo.objects.filter(uname=uname)
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd)
        if s1.hexdigest() == users[0].upwd:
            redit = HttpResponseRedirect('/user/info/')
            # 记住用户名
            if jizhu != 0:
                redit.set_cookie("uname", uname)
            else:
                redit.set_cookie("uname", "", max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return redit
        else:
            context = {"title": "用户登录", "error_name": 0, "error_pwd": 1, "uname": uname, "upwd": upwd}
            return render(request, 'df_user/login.html', context)
    else:
        context = {"title": "用户登录", "error_name": 1, "error_pwd": 0, "uname": uname, "upwd": upwd}
        return render(request, 'df_user/login.html', context)


def info(request):
    users = UserInfo.objects.get(id=request.session['user_id'])
    context = {"title": "用户中心", "users": users}
    return render(request, 'df_user/user_center_info.html', context)


def order(request):
    context = {"title": "用户中心"}
    return render(request, 'df_user/user_center_order.html', context)


def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        user.save()
    context = {"title": "用户中心", "user": user}
    return render(request, 'df_user/user_center_site.html', context)
