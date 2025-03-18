from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail  # 邮件推送
from django.shortcuts import redirect, reverse
from django.http import JsonResponse, Http404  # json返回
from .models import Article, Category, Friendlink, SiteConfig
from datetime import datetime, timedelta  # 日期模块
import random  # 随机模块
import os
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from collections import defaultdict
from itertools import groupby
from operator import attrgetter
from django.conf import settings
from git import Repo

# Create your views here.


def start_page(request):  # 起始页
    return render(request, 'start_page.html')


def index_unlog(request):  # 博客主页
    return render(request, 'index_unlog.html')


def generate_static_pages(request):
    """生成所有静态页面"""
    # 创建git-pages-contents目录（如果不存在）
    if not os.path.exists('blog/git-pages-contents'):
        os.makedirs('blog/git-pages-contents')

    # 创建Jinja2环境
    env = Environment(loader=FileSystemLoader('blog/templates'))

    # 获取所有文章、分类和友链
    articles = Article.objects.all().order_by('-publish_date')
    categories = Category.objects.all()
    friendlinks = Friendlink.objects.all()

    # 为每个分类计算文章数量
    categories_with_count = []
    categories_data = {}

    for category in categories:
        category_articles = articles.filter(category=category)
        category.article_count = category_articles.count()
        categories_with_count.append(category)
        categories_data[category] = category_articles

    # 获取最近的5篇文章
    recent_articles = articles[:5]

    # 获取网站设置
    site_config = SiteConfig.objects.first()

    # 生成首页
    index_template = env.get_template('index.html')
    index_output = index_template.render(
        articles=articles,
        categories=categories_with_count,
        recent_articles=recent_articles,
        friendlinks=friendlinks,
        site_config=site_config
    )

    with open('blog/git-pages-contents/index.html', 'w', encoding='utf-8') as f:
        f.write(index_output)

    # 生成归档页面
    # 按年和月分组文章
    archive_data = defaultdict(lambda: defaultdict(list))

    for article in articles:
        year = article.publish_date.year
        month = article.publish_date.month
        archive_data[year][month].append(article)

    # 对年和月进行排序（降序）
    sorted_archive_data = {}
    for year in sorted(archive_data.keys(), reverse=True):
        sorted_archive_data[year] = {}
        for month in sorted(archive_data[year].keys(), reverse=True):
            sorted_archive_data[year][month] = archive_data[year][month]

    archive_template = env.get_template('archive.html')
    archive_output = archive_template.render(
        archive_data=sorted_archive_data,
        categories=categories_with_count,
        recent_articles=recent_articles,
        site_config=site_config
    )

    with open('blog/git-pages-contents/archive.html', 'w', encoding='utf-8') as f:
        f.write(archive_output)

    # 生成分类页面
    categories_template = env.get_template('categories.html')
    categories_output = categories_template.render(
        categories_data=categories_data,
        categories=categories_with_count,
        recent_articles=recent_articles,
        site_config=site_config
    )

    with open('blog/git-pages-contents/categories.html', 'w', encoding='utf-8') as f:
        f.write(categories_output)

    # 生成友链页面
    friends_template = env.get_template('friends.html')
    friends_output = friends_template.render(
        friendlinks=friendlinks,
        categories=categories_with_count,
        recent_articles=recent_articles,
        site_config=site_config
    )

    with open('blog/git-pages-contents/friends.html', 'w', encoding='utf-8') as f:
        f.write(friends_output)

    # 生成关于页面
    about_template = env.get_template('about.html')
    about_output = about_template.render(
        categories=categories_with_count,
        recent_articles=recent_articles,
        site_config=site_config
    )

    with open('blog/git-pages-contents/about.html', 'w', encoding='utf-8') as f:
        f.write(about_output)

    # 生成每篇文章的HTML
    article_template = env.get_template('article.html')

    for article in articles:
        # 获取上一篇和下一篇文章
        prev_article = article.prev_article()
        next_article = article.next_article()

        # 将Markdown转换为HTML
        html_content = markdown(article.content)

        # 渲染模板
        output = article_template.render(
            content=html_content,
            title=article.title,
            category=article.category,
            publish_date=article.publish_date,
            prev_article=prev_article,
            next_article=next_article,
            site_config=site_config
        )

        # 创建分类目录（如果不存在）
        category_path = os.path.join(
            'blog/git-pages-contents', article.category.cat_name)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

        # 保存文件
        with open(os.path.join(category_path, f'{article.title}.html'), 'w', encoding='utf-8') as f:
            f.write(output)

    # 如果上传了favicon，复制到静态目录
    if site_config and site_config.favicon:
        import shutil
        favicon_path = os.path.join('blog/git-pages-contents', 'favicon.ico')
        shutil.copy2(site_config.favicon.path, favicon_path)

    # 如果启用了自动Git推送，则推送到GitHub Pages
    if settings.ENABLE_AUTO_GIT_PUSH:
        try:
            repo_path = 'blog/git-pages-contents'
            repo = Repo(repo_path)
            repo.git.add(A=True)  # 添加所有文件
            repo.index.commit('更新博客内容')
            origin = repo.remote(name=settings.GITHUB_PAGES_REPO)
            origin.push(
                refspec=f'{settings.GITHUB_PAGES_BRANCH}:{settings.GITHUB_PAGES_BRANCH}')
            return JsonResponse({'status': 'success', 'message': '静态页面生成并推送成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Git推送失败: {str(e)}'})

    return JsonResponse({'status': 'success', 'message': '静态页面生成成功'})
