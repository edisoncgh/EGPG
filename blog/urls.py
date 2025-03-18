from django.urls import path
from django.conf.urls import url, include

from . import views

# 为 URL 名称添加命名空间
app_name = 'blog'
urlpatterns = [
    # 博客子系统默认页面路由
    # ex: blog/
    path('', views.start_page, name='start_page'),
    path('index/', views.index_unlog, name='index_unlog'),
    path('generate/', views.generate_static_pages, name='generate_static_pages'),
    # 博客子系统登录界面路由
    # ex: blog/login
    # path('login', views.login, name='login'),
]
