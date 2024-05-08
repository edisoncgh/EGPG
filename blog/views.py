from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail  # 邮件推送
from django.shortcuts import redirect, reverse
from django.http import JsonResponse  # json返回
from .models import Article, Category
from datetime import datetime, timedelta  # 日期模块
import random  # 随机模块

# Create your views here.
def start_page(request):  # 起始页
    return render(request, 'start_page.html')

def index_unlog(request):  # 博客主页
    # try:
    #     article_list = Article.objects.order_by('-publish_date')
    #     context = {'article_list': article_list}
    # except Article.DoesNotExist:
    #     raise Http404("这里还没有文章喔")
    # return render(request, 'index_unlog.html', context)
    return render(request, 'index_unlog.html')