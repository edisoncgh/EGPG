# EGPG:EdisonGithubPagesGenerator
一个使用`python django`编写的用于维护github pages静态博客的静态页面生成器。
### Motivation
个人搭建博客最大的成本就是服务器开销，github pages可以很好地帮助每一个coder避免这一部分成本。但是诸如docsify、vuepress的静态文档管理框架有些**过于静态**了，一些轻微响应化的行为（诸如归档页面、文章分类、友链添加、博客首页）都需要自己手动配置响应的文档页面，这未免太麻烦了。正好本人曾经稍微浅尝过`django`，`python`也是我目前的主力工作语言，就搞了这么一个静态页面生成、维护工具。
### Introduction
正如简介所言，这是一个使用`python django`编写的用于维护github pages静态博客的静态页面生成器。
主要特性包括：
- 集成了支持实时可视化的Markdown编辑插件
- 文章在后台完成编辑后自动渲染为静态html文件，支持模版自定义，默认保存路径为`blog\git-pages-contents`，并且**即将支持**生成完成的静态页面同步`push`到git pages仓库
- 博客首页动态添加最近博文，所有博文在首页按时间顺序排序
- ~~博文页面支持跳转到上/下一篇~~
- 支持友链功能
- 支持归档页面
- 支持按照Category对博文进行分类，未分类的博文默认生成在`Unclassified`目录下
暂时就这么多
### 使用
将项目clone到本地之后，在`EGPG`目录下运行`py manage.py runserver 8080`(也可以是随便哪个没有被占用的端口)即可