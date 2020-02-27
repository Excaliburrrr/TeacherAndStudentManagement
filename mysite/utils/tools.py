# _*_ coding: utf-8 _*_
# Author: Sebuntin
# Time: 16:21
# Name: tools.py
from django.shortcuts import redirect

def verify(urls_func):
    """闭包函数，用来验证cookie"""
    def wrap(request):
        # 装饰带参函数时，如果参数确定，则直接在内部函数中给定
        try:
            tk =  request.get_signed_cookie("ticket", salt="hhhhhh")
        except Exception:
            return redirect("/login/")
        else:
            if tk:
                return urls_func(request)
            else:
                return redirect("/login/")
    return wrap


