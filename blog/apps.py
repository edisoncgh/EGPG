from django.apps import AppConfig
import os


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        # 确保必要的目录存在
        directories = [
            'blog/git-pages-contents',
            'blog/static/media',
            'blog/static/media/uploads',
            'blog/static/media/editor',
            'blog/management/commands',
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # 确保management/commands目录中有__init__.py文件
        init_files = [
            'blog/management/__init__.py',
            'blog/management/commands/__init__.py',
        ]

        for init_file in init_files:
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass  # 创建空文件
