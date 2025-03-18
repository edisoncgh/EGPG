import hashlib  # 哈希库
from django.db import models, transaction
from django.utils import timezone
from django.contrib import admin
from mdeditor.fields import MDTextField
from django.conf import settings

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
import os
from git import Repo


# ========================== category ==========================
# 定义一个函数来获取默认分类ID
def get_default_category():
    category, created = Category.objects.get_or_create(cat_name='未分类')
    return category.cat_id


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
    # 修改 category 字段，使用 get_default_category 函数
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name='文章分类', null=False,
        default=get_default_category  # 使用函数引用而不是 lambda
    )
    article_id = models.AutoField(
        verbose_name='文章ID',
        primary_key=True
    )  # 修改为 AutoField
    # 因为创建静态文件依赖博文标题，所以文章标题不可重复
    title = models.CharField(
        verbose_name='标题', max_length=50, default='无题', unique=True)
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
    def next_article(self):
        # 增加错误处理
        if self.article_id is None:
            return None
        return Article.objects.filter(
            article_id__gt=self.article_id
        ).order_by('article_id').first()

    # 前一篇
    def prev_article(self):
        # 增加错误处理
        if self.article_id is None:
            return None
        return Article.objects.filter(
            article_id__lt=self.article_id
        ).order_by('-article_id').first()

    # 模型元数据选项
    class Meta:
        db_table = "articles"  # 数据库表名
        ordering = ['-publish_date']  # 按发布日志降序排序
        verbose_name = '文章'  # 指定后台显示模型名称
        verbose_name_plural = '所有文章'  # 指定后台显示模型复数名称

# ========================== 友链 ==========================


class Friendlink(models.Model):
    link_id = models.AutoField(
        verbose_name='友链ID',
        primary_key=True
    )
    link_url = models.URLField(
        verbose_name='友链地址'
    )
    link_desc = models.CharField(
        verbose_name='友链描述',
        max_length=100
    )
    link_name = models.CharField(
        verbose_name='友链名称',
        max_length=20
    )
    link_email = models.EmailField(
        verbose_name='友链邮箱',
        help_text='用于生成默认头像，不会公开显示',
        blank=True,
        null=True
    )
    link_avatar = models.ImageField(
        verbose_name='友链头像',
        upload_to='uploads/',
        blank=True,
        null=True
    )

    def get_avatar_url(self):
        if self.link_avatar and hasattr(self.link_avatar, 'url'):
            return self.link_avatar.url

        # 如果没有上传头像，使用 QQ 邮箱头像服务或 cravatar
        if self.link_email:
            # 生成邮箱的 MD5 值
            email_hash = hashlib.md5(
                self.link_email.lower().encode('utf-8')).hexdigest()

            # 如果是 QQ 邮箱，使用 QQ 头像
            if self.link_email.endswith('@qq.com'):
                qq_number = self.link_email.split('@')[0]
                return f'https://q1.qlogo.cn/g?b=qq&nk={qq_number}&s=100'

            # 否则使用 cravatar（Gravatar 的国内镜像）
            return f'https://cravatar.cn/avatar/{email_hash}?d=mp&s=200'

        # 如果既没有头像也没有邮箱，返回默认头像
        return 'https://cravatar.cn/avatar/default?d=mp&s=200'

    def __str__(self):
        if self.link_name:
            return self.link_name
        else:
            return 'empty'

    class Meta:
        db_table = "friendlinks"
        verbose_name = '友链'
        verbose_name_plural = '所有友链'

# 基于django信号机制，当文章保存时，将Markdown渲染为HTML，并保存为静态文件
# 监听Article模型的post_save信号


@receiver(post_save, sender=Article)
def create_html_file(sender, instance, **kwargs):
    # 使用事务装饰器确保数据库操作的原子性
    @transaction.atomic
    def generate_html():
        try:
            print(f'============监听到文章{instance.title}保存信号============')
            # 创建一个 Jinja2 环境
            env = Environment(loader=FileSystemLoader('blog/templates'))

            # 确保git-pages-contents目录存在
            if not os.path.exists('blog/git-pages-contents'):
                os.makedirs('blog/git-pages-contents')

            # 加载模板
            template = env.get_template('article.html')

            # 获取上一篇和下一篇文章（在事务中进行）
            prev_article = instance.prev_article()
            next_article = instance.next_article()

            # 将 Markdown 转换为 HTML
            html_content = markdown(instance.content or '')

            # 渲染模板
            output = template.render(
                content=html_content,
                title=instance.title,
                category=instance.category,
                publish_date=instance.publish_date,
                prev_article=prev_article,
                next_article=next_article
            )

            # 创建分类目录
            category_path = os.path.join('blog/git-pages-contents',
                                         instance.category.cat_name)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

            # 保存文件
            file_path = os.path.join(category_path, f'{instance.title}.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(output)

            # Git 推送部分
            config = GitConfig.objects.first()
            if config and config.enable_auto_push:
                try:
                    auth_url = config.get_auth_url()
                    if not auth_url:
                        print("Git配置不完整，跳过推送")
                        return

                    repo_path = 'blog/git-pages-contents'
                    repo = Repo(repo_path)

                    # 配置Git
                    with repo.config_writer() as git_config:
                        # 基本配置
                        git_config.set_value('http', 'version', 'HTTP/1.1')
                        git_config.set_value('core', 'askPass', '')
                        git_config.set_value('credential', 'helper', '')

                        # 网络相关配置
                        git_config.set_value('http', 'postBuffer', '524288000')
                        git_config.set_value('core', 'compression', '0')
                        git_config.set_value('http', 'sslVerify', 'false')

                        # 超时和重试设置
                        git_config.set_value('http', 'lowSpeedLimit', '1000')
                        git_config.set_value('http', 'lowSpeedTime', '60')
                        git_config.set_value('core', 'packedGitLimit', '512m')
                        git_config.set_value(
                            'core', 'packedGitWindowSize', '512m')
                        git_config.set_value('pack', 'windowMemory', '512m')
                        git_config.set_value('pack', 'packSizeLimit', '512m')

                    # 更新远程URL
                    try:
                        origin = repo.remote('origin')
                        current_url = origin.url
                        if current_url != auth_url:
                            origin.set_url(auth_url)
                            print(f"更新远程URL: {auth_url}")
                    except ValueError:
                        repo.create_remote('origin', auth_url)
                        print(f"创建新的远程URL: {auth_url}")

                    # 添加并提交更改
                    repo.index.add(['.'])
                    repo.index.commit(f'添加博文："{instance.title}"')

                    # 推送前先尝试拉取
                    try:
                        origin = repo.remote('origin')
                        origin.fetch()
                        origin.pull(config.repo_branch)
                    except Exception as e:
                        print(f"拉取更新失败（非致命错误）：{str(e)}")

                    # 推送（带重试）
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            print(f"尝试第 {attempt + 1} 次推送...")
                            origin = repo.remote('origin')
                            # 使用force选项
                            origin.push(
                                refspec=f'{config.repo_branch}:{config.repo_branch}', force=True)
                            print(f'=================== 推送成功 ===================')
                            break
                        except Exception as e:
                            print(f'第 {attempt + 1} 次推送失败：{str(e)}')
                            if attempt == max_retries - 1:
                                raise
                            import time
                            time.sleep(5 * (attempt + 1))  # 增加等待时间

                except Exception as e:
                    print(f'推送失败：{str(e)}')

        except Exception as e:
            print(f'生成HTML文件时发生错误：{str(e)}')
            # 不抛出异常，确保文章能够保存
            pass

    # 在事务外执行文件操作
    transaction.on_commit(generate_html)

# 基于django信号机制，当文章删除时，同步删除同命静态文件
# 监听Article模型的post_delete信号


@receiver(post_delete, sender=Article)
def delete_html_file(sender, instance, **kwargs):
    try:
        # 构造文件路径
        if instance.category.cat_name != '未分类':
            file_path = os.path.join(
                f'blog/git-pages-contents/{instance.category.cat_name}', f'{instance.title}.html')
        else:
            file_path = os.path.join(
                f'blog/git-pages-contents/未分类', f'{instance.title}.html')

        # 检查文件是否存在
        if os.path.isfile(file_path):
            # 删除文件
            os.remove(file_path)
            print(f'成功删除文件: {file_path}')
        else:
            print(f'文件不存在: {file_path}')

        # 创建git对象
        repo_path = 'blog/git-pages-contents'
        repo = Repo(repo_path)

        # 检查是否开启自动推送
        config = GitConfig.objects.first()
        if config and config.enable_auto_push:
            auth_url = config.get_auth_url()
            if auth_url:
                try:
                    # 确保远程仓库配置正确
                    try:
                        origin = repo.remote('origin')
                        if origin.url != auth_url:
                            origin.set_url(auth_url)
                    except ValueError:
                        repo.create_remote('origin', auth_url)

                    # 提交更改
                    repo.index.add(['.'])
                    repo.index.commit(f'删除博文："{instance.title}"')

                    # 推送更改
                    origin = repo.remote('origin')
                    origin.push(
                        refspec=f'{config.repo_branch}:{config.repo_branch}')
                    print(f'=================== 推送成功 ===================')
                except Exception as e:
                    print(f'推送失败：{str(e)}')
    except Exception as e:
        print(f'删除文件时发生错误：{str(e)}')


class GitConfig(models.Model):
    enable_auto_push = models.BooleanField(
        verbose_name='启用自动推送',
        default=False
    )
    repo_url = models.URLField(
        verbose_name='GitHub Pages仓库URL',
        help_text='使用HTTPS格式，例如：https://github.com/username/username.github.io.git',
        blank=True
    )
    repo_branch = models.CharField(
        verbose_name='推送分支',
        max_length=50,
        default='master',
        help_text='通常是master或main'
    )
    github_token = models.CharField(
        verbose_name='GitHub Personal Access Token',
        max_length=100,
        help_text='从GitHub设置页面生成的个人访问令牌（需要repo权限）',
        blank=True
    )

    class Meta:
        verbose_name = 'Git配置'
        verbose_name_plural = 'Git配置'

    def get_auth_url(self):
        """获取带认证信息的URL"""
        if not self.repo_url or not self.github_token:
            return None

        # 清理URL，确保格式正确
        clean_url = self.repo_url.replace('@', '').strip()
        if not clean_url.startswith('https://github.com/'):
            return None

        # 从URL中提取仓库路径
        repo_path = clean_url.replace('https://github.com/', '')

        # 构造新的认证URL
        return f'https://{self.github_token}@github.com/{repo_path}'

    def save(self, *args, **kwargs):
        # 清理URL
        if self.repo_url:
            self.repo_url = self.repo_url.replace('@', '').strip()
        super().save(*args, **kwargs)


class SiteConfig(models.Model):
    site_name = models.CharField(
        verbose_name='网站名称',
        max_length=100,
        default='我的博客'
    )
    favicon = models.ImageField(
        verbose_name='网站图标',
        upload_to='favicon/',
        help_text='建议上传 .ico 格式的图标文件，尺寸为 32x32 或 16x16 像素',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'

    def __str__(self):
        return self.site_name
