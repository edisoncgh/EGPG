from django.contrib import admin

from .models import Article, Category, Friendlink
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


admin.site.register(Article, ArticleAdmin)


class CategoryAdmin(admin.ModelAdmin):  # 类别管理面板
    fields = ['cat_name']
    # 展示形式
    list_display = ('add_date', 'cat_name')
    # 按类别名称搜索的搜索框
    search_fields = ['cat_name']


admin.site.register(Category, CategoryAdmin)

class FriendlinkAdmin(admin.ModelAdmin):  # 友链管理面板
    fields = ['link_name', 'link_url', 'link_desc', 'link_avatar']
    # 展示形式
    list_display = ('link_name', 'link_url', 'link_desc')
    # 按类别名称搜索的搜索框
    search_fields = ['link_name']


admin.site.register(Friendlink, FriendlinkAdmin)