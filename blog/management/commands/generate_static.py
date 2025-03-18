from django.core.management.base import BaseCommand
from blog.views import generate_static_pages
from django.test.client import RequestFactory


class Command(BaseCommand):
    help = '生成静态博客页面并推送到GitHub Pages'

    def handle(self, *args, **options):
        self.stdout.write('开始生成静态页面...')

        # 创建一个模拟的请求对象
        factory = RequestFactory()
        request = factory.get('/generate/')

        # 调用生成静态页面的视图函数
        response = generate_static_pages(request)

        # 检查响应
        if response.status_code == 200:
            import json
            result = json.loads(response.content)
            if result.get('status') == 'success':
                self.stdout.write(self.style.SUCCESS('静态页面生成成功！'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'静态页面生成失败: {result.get("message")}'))
        else:
            self.stdout.write(self.style.ERROR(
                f'静态页面生成失败，HTTP状态码: {response.status_code}'))
