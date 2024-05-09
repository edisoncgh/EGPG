import hashlib  # 哈希库
from django.db import models
from django.utils import timezone
from django.contrib import admin
from mdeditor.fields import MDTextField

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
import os

# ========================== category ==========================
class Category(models.Model):
    cat_id = models.AutoField(verbose_name='类别id', primary_key=True)  # 主键，自增
    cat_name = models.CharField(
        verbose_name='类别名称', max_length=20, null=False, default='未分类')
    add_date = models.DateTimeField(
        verbose_name='添加日期', default=timezone.now)

    # 使对象在后台显示更友好
    def __str__(self):
        if self.cat_name:
            return self.cat_name
        else:
            return "empty field"

    # 模型元数据选项
    class Meta:
        db_table = "categories"  # 数据库表名
        verbose_name = '类别'  # 指定后台显示模型名称
        verbose_name_plural = '所有类别'  # 指定后台显示模型复数名称

# 创建默认分类
default_category = Category.objects.get(cat_name='未分类').pk

# ========================== article ==========================
class Article(models.Model):
    SMALL_TALK = 'sm'
    BLOG_ARTICLE = 'lg'
    CONTENT_TYPE_CHOICE = (
        (SMALL_TALK, '说说'),
        (BLOG_ARTICLE, '博文')
    )

    content_type = models.CharField(
        max_length=5,
        choices=CONTENT_TYPE_CHOICE,
        default=BLOG_ARTICLE,
        verbose_name='内容类型'
    )  # 内容类型，默认为博文
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name='文章分类', null=False, default=default_category)  # 外键，指向所属分类
    article_id = models.IntegerField(
        verbose_name='文章ID', primary_key=True)  # 主键，自增
    # 因为创建静态文件依赖博文标题，所以文章标题不可重复
    title = models.CharField(verbose_name='标题', max_length=50, default='无题', unique=True)
    content = MDTextField(verbose_name='正文', blank=True, null=True)
    publish_date = models.DateTimeField(
        verbose_name='发布日期', default=timezone.now, editable=False)
    comment_num = models.PositiveIntegerField(
        verbose_name='评论数', default=0, editable=False)
    like_num = models.PositiveIntegerField(
        verbose_name='点赞数', default=0, editable=False)
    visit_num = models.PositiveIntegerField(
        verbose_name='浏览数', default=0, editable=False)

    # 使对象在后台显示更友好
    def __str__(self):
        if self.title:
            return self.title
        else:
            return 'empty'

    # 更新浏览量
    def visited(self):
        self.visit_num += 1
        self.save(update_fields=['visit_num'])

    # 更新点赞
    def liked(self):
        self.like_num += 1
        self.save(update_fields=['like_num'])

    # 下一篇
    def next_article(self):  # id比当前id大，状态为已发布，发布时间不为空
        return Article.objects.filter(id__gt=self.article_id, pub_time__isnull=False).first()

    # 前一篇
    def prev_article(self):  # id比当前id小，状态为已发布，发布时间不为空
        return Article.objects.filter(id__lt=self.article_id, pub_time__isnull=False).first()

    # 模型元数据选项
    class Meta:
        db_table = "articles"  # 数据库表名
        ordering = ['-publish_date']  # 按发布日志降序排序
        verbose_name = '文章'  # 指定后台显示模型名称
        verbose_name_plural = '所有文章'  # 指定后台显示模型复数名称

# ========================== 友链 ==========================

class Friendlink(models.Model):
    link_id = models.AutoField(
        verbose_name='友链ID', primary_key=True)  # 主键，自增
    link_url = models.URLField(
        verbose_name='友链地址')
    link_desc = models.CharField(
        verbose_name='友链描述', max_length=100)
    link_name = models.CharField(
        verbose_name='友链名称', max_length=20)
    # 图片会被上传至MEDIA_ROOT / uploads
    # MEDIA_ROOT = BASE_DIR / blog / static / media
    link_avatar = models.ImageField(
        verbose_name='友链头像',
        upload_to='uploads/',  # 媒体文件路径会添加到 MEDIA_ROOT 下
        default="default.jpg"  # 默认图片路径相对于 upload_to
    )

    # 使对象在后台显示更友好
    def __str__(self):
        if self.link_name:
            return self.link_name
        else:
            return 'empty'

    # 模型元数据选项
    class Meta:
        db_table = "friendlinks"  # 数据库表名
        verbose_name = '友链'  # 指定后台显示模型名称
        verbose_name_plural = '所有友链'  # 指定后台显示模型复数名称

# 基于django信号机制，当文章保存时，将Markdown渲染为HTML，并保存为静态文件
# 监听Article模型的post_save信号
@receiver(post_save, sender=Article)
def create_html_file(sender, instance, **kwargs):
    print(f'============监听到文章{instance.title}保存信号============')
    # 创建一个 Jinja2 环境
    env = Environment(loader=FileSystemLoader('blog/templates'))

    # 加载你的模板
    template = env.get_template('test.html')

    # 将 Markdown 转换为 HTML
    html_content = markdown(instance.content)

    # 渲染模板
    output = template.render(
        content=html_content, 
        title=instance.title, 
        category=instance.category if instance.category else None, 
        publish_date=instance.publish_date
    )

    # with open(os.path.join('blog/git-pages-contents/Unclassified', f'{instance.title}.html'), 'w', encoding='utf-8') as f:
    #         f.write(output)

    # 创建分类目录
    if instance.category.cat_name != '未分类':
        if not os.path.exists(os.path.join('blog/git-pages-contents', instance.category.cat_name)):
            os.makedirs(os.path.join('blog/git-pages-contents', instance.category.cat_name))
            # 将渲染后的 HTML 写入文件，按分类存储
            with open(os.path.join(f'blog/git-pages-contents/{instance.category.cat_name}', f'{instance.title}.html'), 'w', encoding='utf-8') as f:
                print(f'======blog/git-pages-contents/{instance.category.cat_name}/{instance.title}.html======')
                f.write(output)
    # 如果没有分类，就直接放在未分类目录
    else:
        if not os.path.exists(os.path.join('blog/git-pages-contents', instance.category.cat_name)):
            # 创建未分类目录
            os.makedirs(os.path.join('blog/git-pages-contents', '未分类'))
        with open(os.path.join('blog/git-pages-contents/未分类', f'{instance.title}.html'), 'w', encoding='utf-8') as f:
            f.write(output)

# 基于django信号机制，当文章删除时，同步删除同命静态文件
# 监听Article模型的post_delete信号
@receiver(post_delete, sender=Article)
def delete_html_file(sender, instance, **kwargs):
    if instance.category.cat_name != '未分类':
        # 构造文件路径
        file_path = os.path.join(f'blog/git-pages-contents/{instance.category.cat_name}', f'{instance.title}.html')
    else:
        file_path = os.path.join(f'blog/git-pages-contents/未分类', f'{instance.title}.html')
    # 检查文件是否存在
    if os.path.isfile(file_path):
        # 删除文件
        os.remove(file_path)