"""demo02 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path,include
from django.conf.urls import url,include

urlpatterns = [
    #url(r'^myexcel/$',views.MyExcelView.as_view()),
    #path('myexcel/',views.MyExcelView.as_view()),
]
router = DefaultRouter()  # 创建路由器(路由器只能结束视图集一起使用) 默认只为标准了增删改查行为生成路由信息,如果想让自定义的行为也生成路由需要在自定义行为上用action装饰进行装饰
router.register(r'user', views.MyExcelView)  # 注册路由
urlpatterns += router.urls  # 把生成好的路由拼接到urlpatterns