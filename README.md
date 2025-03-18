# Edison GitHub Pages Generator (EGPG)

EGPG 是一个基于 Django 3.2.20 开发的静态博客页面生成器，专为 GitHub Pages 设计。它提供了一个功能丰富的后台管理系统，让您可以轻松管理和发布博客内容。

## 主要特性

### 1. 内容管理
- **双重内容类型**：支持发布"博文"和"说说"两种类型的内容
- **Markdown 编辑器**：集成 MDEditor，支持 Markdown 格式编写文章
- **文章分类**：支持文章分类管理，自动创建"未分类"作为默认分类
- **文章统计**：自动统计文章的访问量、评论数和点赞数
- **文章导航**：支持上一篇/下一篇文章导航功能

### 2. 友情链接管理
- **智能头像系统**：
  - 支持自定义上传头像
  - 自动识别 QQ 邮箱并调用 QQ 头像服务
  - 支持 Gravatar 头像（使用国内镜像 cravatar.cn）
  - 提供默认头像兜底方案
- **完整信息管理**：支持管理友链的名称、描述、URL 等信息

### 3. GitHub Pages 集成
- **自动部署**：支持自动将生成的静态页面推送到 GitHub Pages 仓库
- **灵活配置**：
  - 可配置是否启用自动推送
  - 支持自定义仓库 URL 和分支
  - 支持 GitHub Personal Access Token 认证
- **手动控制**：提供手动推送按钮，随时更新站点内容

### 4. 网站个性化
- **网站图标**：支持自定义网站 favicon
- **网站标题**：可自定义网站名称
- **响应式设计**：适配各种设备屏幕

## 使用指南

### 1. 基础配置
1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 初始化数据库：
```bash
python manage.py makemigrations
python manage.py migrate
```

3. 创建超级用户：
```bash
python manage.py createsuperuser
```

### 2. 文章管理
1. 访问 `/admin` 进入管理后台
2. 在"所有文章"中可以：
   - 创建新文章（博文/说说）
   - 选择文章分类
   - 使用 Markdown 编辑器编写内容
   - 查看文章统计数据

### 3. 友情链接配置
1. 在管理后台的"所有友链"中添加新的友情链接
2. 填写必要信息：
   - 友链名称
   - 网站地址
   - 网站描述
   - 头像配置：
     - 上传自定义头像
     - 或填写邮箱（推荐 QQ 邮箱）自动获取头像

### 4. GitHub Pages 设置
1. 在管理后台找到"Git配置"
2. 配置以下信息：
   - GitHub Pages 仓库地址
   - 推送分支（通常是 master 或 main）
   - GitHub Personal Access Token
   - 是否启用自动推送
3. 使用"手动推送"按钮测试配置是否正确

### 5. 网站个性化设置
1. 在"网站设置"中配置：
   - 网站名称
   - 上传网站图标（favicon）
2. 所有更改后需要重新生成静态页面并推送到 GitHub Pages

### 6. 静态页面生成
- 自动生成：启用自动推送后，内容更新时自动生成并推送
- 手动生成：
  1. 在管理后台点击"生成静态页面"按钮
  2. 或访问 `/generate/` 路径触发生成

## 注意事项
1. 确保 GitHub Personal Access Token 具有足够的仓库权限
2. 文章标题不可重复，因为它们用于生成静态文件名
3. 上传的 favicon 建议使用 .ico 格式，尺寸为 32x32 或 16x16 像素
4. 更改模板后需要手动重新生成静态页面
5. 删除文章时会自动删除对应的静态文件

## 技术栈
- Django 3.2.20
- Bootstrap 5.1.3
- Python Markdown
- MDEditor
- SimpleUI（后台美化）
- GitPython（Git 操作）
- Jinja2（模板引擎）

## 许可证
MIT License