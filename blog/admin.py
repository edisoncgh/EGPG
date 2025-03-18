from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from .models import Article, Category, Friendlink, GitConfig, SiteConfig
import os
from git import Repo
import time

# Register your models here.


class ArticleAdmin(admin.ModelAdmin):  # 文章管理面板
    fields = ['content_type', 'title', 'content', 'category']
    # 后台展示方式
    list_display = ('content_type', 'title', 'publish_date', 'category', 'visit_num',
                    'comment_num', 'like_num')
    # 按日期筛选
    list_filter = ['publish_date']
    # 按标题搜索的搜索框
    search_fields = ['title']

    # 添加生成静态页面的按钮
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_static_pages/', self.admin_site.admin_view(
                self.generate_static_pages_view), name='generate_static_pages'),
        ]
        return custom_urls + urls

    def generate_static_pages_view(self, request):
        # 重定向到生成静态页面的视图
        return redirect('generate_static_pages')

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            self.message_user(request, f"保存文章时发生错误：{str(e)}", level='ERROR')
            raise  # 重新抛出异常，确保事务回滚


admin.site.register(Article, ArticleAdmin)


class CategoryAdmin(admin.ModelAdmin):  # 类别管理面板
    fields = ['cat_name']
    # 展示形式
    list_display = ('add_date', 'cat_name')
    # 按类别名称搜索的搜索框
    search_fields = ['cat_name']


admin.site.register(Category, CategoryAdmin)


class FriendlinkAdmin(admin.ModelAdmin):  # 友链管理面板
    fields = ['link_name', 'link_url',
              'link_desc', 'link_email', 'link_avatar']
    # 展示形式
    list_display = ('link_name', 'link_url', 'link_desc')
    # 按类别名称搜索的搜索框
    search_fields = ['link_name']


admin.site.register(Friendlink, FriendlinkAdmin)

# 注册git push设置


class GitConfigAdmin(admin.ModelAdmin):
    list_display = ('enable_auto_push', 'repo_url', 'repo_branch')
    actions = None  # 禁用批量操作

    def has_add_permission(self, request):
        # 只允许存在一条配置记录
        return not GitConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('manual_push/',
                 self.admin_site.admin_view(self.manual_push_view),
                 name='git_manual_push'),
        ]
        return custom_urls + urls

    def manual_push_view(self, request):
        try:
            config = GitConfig.objects.first()
            if not config:
                messages.error(request, '请先添加Git配置')
                return redirect('..')

            auth_url = config.get_auth_url()
            if not auth_url:
                messages.error(request, '请确保已配置正确的仓库URL和GitHub Token')
                return redirect('..')

            repo_path = 'blog/git-pages-contents'
            repo = Repo(repo_path)

            # 配置Git
            with repo.config_writer() as git_config:
                git_config.set_value('http', 'version', 'HTTP/1.1')
                git_config.set_value('core', 'askPass', '')
                git_config.set_value('credential', 'helper', '')

            # 更新远程URL
            try:
                origin = repo.remote('origin')
                origin.set_url(auth_url)
            except ValueError:
                repo.create_remote('origin', auth_url)

            # 添加并提交更改
            repo.git.add(A=True)
            repo.index.commit('手动更新博客内容')

            # 推送（带重试）
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    origin = repo.remote('origin')
                    origin.push(
                        refspec=f'{config.repo_branch}:{config.repo_branch}')
                    messages.success(request, '手动推送成功！')
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        messages.error(request, f'推送失败：{str(e)}')
                        break
                    time.sleep(2 ** attempt)

        except Exception as e:
            messages.error(request, f'操作失败：{str(e)}')

        return redirect('..')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_manual_push'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context)


admin.site.register(GitConfig, GitConfigAdmin)

# 自定义管理站点


class CustomAdminSite(admin.AdminSite):
    site_header = '博客管理系统'
    site_title = '博客管理'
    index_title = '管理面板'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate_static_pages/', self.admin_view(self.generate_static_pages_view),
                 name='admin_generate_static_pages'),
        ]
        return custom_urls + urls

    def generate_static_pages_view(self, request):
        # 重定向到生成静态页面的视图
        return redirect('generate_static_pages')


# 替换默认的admin站点
admin_site = CustomAdminSite(name='customadmin')
admin_site.register(Article, ArticleAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(Friendlink, FriendlinkAdmin)


class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('site_name',)

    def has_add_permission(self, request):
        # 只允许存在一条配置记录
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(SiteConfig, SiteConfigAdmin)
