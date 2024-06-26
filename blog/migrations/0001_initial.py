# Generated by Django 3.2.20 on 2024-05-07 01:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mdeditor.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('cat_id', models.AutoField(primary_key=True, serialize=False, verbose_name='类别id')),
                ('cat_name', models.CharField(max_length=20, verbose_name='类别名称')),
                ('add_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加日期')),
            ],
            options={
                'verbose_name': '类别',
                'verbose_name_plural': '所有类别',
                'db_table': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('content_type', models.CharField(choices=[('sm', '说说'), ('lg', '博文')], default='lg', max_length=5, verbose_name='内容类型')),
                ('article_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='文章ID')),
                ('title', models.CharField(default='无题', max_length=50, verbose_name='标题')),
                ('content', mdeditor.fields.MDTextField(blank=True, null=True, verbose_name='正文')),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='发布日期')),
                ('comment_num', models.PositiveIntegerField(default=0, editable=False, verbose_name='评论数')),
                ('like_num', models.PositiveIntegerField(default=0, editable=False, verbose_name='点赞数')),
                ('visit_num', models.PositiveIntegerField(default=0, editable=False, verbose_name='浏览数')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='blog.category', verbose_name='文章分类')),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '所有文章',
                'db_table': 'articles',
                'ordering': ['-publish_date'],
            },
        ),
    ]
