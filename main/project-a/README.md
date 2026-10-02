# 工程题A：文章管理系统（数据层）

基于 Django 实现的文章管理系统数据层，涵盖数据模型设计、附件管理、信号驱动操作审计、并发安全浏览量统计等核心功能。

## 功能清单

### 必选功能
1. **数据模型设计**（`article/models.py`）
   - `Article` 文章：标题、正文、作者外键、状态（草稿/已发布/已归档）、浏览量、创建/更新时间
   - `Attachment` 附件：文件名、文件字段、关联文章外键、上传时间
   - `AuditLog` 审计日志：操作类型、关联文章外键、操作人外键、时间戳、JSON 变更摘要
   - 均配置 `__str__`、`Meta`（verbose_name、排序）
2. **附件管理**
   - 登录用户可为自己的文章上传附件，文件存放于 `MEDIA_ROOT/attachments/`
   - 文章详情页展示附件列表，作者可删除自己的附件
   - 配置了 `MEDIA_URL` / `MEDIA_ROOT`，开发环境可通过 `/media/` 访问媒体文件
3. **信号驱动操作审计**
   - 使用 Django 信号 `post_save` / `pre_delete` 自动生成 `AuditLog`，视图层不手动创建审计日志
   - JSON `diff` 字段记录字段变更前后差异（如状态 old/new）
   - 文章详情页倒序展示对应审计日志
4. **并发安全浏览量**
   - 访问详情页浏览量自增，使用 **F 表达式** 在数据库层原子更新
   - 代码注释解释「直接对象自增 + save」在并发下发生丢失更新的问题

### 已实现的加分项
1. **软删除**：删除文章仅置 `is_deleted=True`，不物理删除记录，列表过滤已删数据，审计日志保留
2. **统计页面 `/stats/`**：展示文章总量、总浏览量、各状态文章数量、最近 10 条审计日志
3. **附件下载计数**：下载时使用 F 表达式原子 +1，页面展示下载次数

> 说明：封面缩略图加分项（Pillow 生成 200px 缩略图）如需要可补充。

## 环境要求
- Python 3.12+（本机实测 Django 4.2.30 + Python 3.14 可运行；官方支持范围以 Django 文档为准）
- 依赖见 `requirements.txt`

## 安装与启动

```bash
pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 访问地址
- 管理后台：http://127.0.0.1:8000/admin/
- 文章列表：http://127.0.0.1:8000/articles/
- 文章详情：http://127.0.0.1:8000/article/<id>/
- 统计页面：http://127.0.0.1:8000/stats/

## 自动化自测
```bash
# 数据层自测（信号审计、F 浏览量、软删除、附件计数、统计）
py manage.py shell -c "exec(open('tests/selftest.py', encoding='utf-8').read())"

# 端到端 HTTP 自测（需先 runserver，且存在 tester/testpass123 用户）
py tests/e2e_test.py
```

## 工程说明
1. 开发在功能分支 `feature/article-data-layer` 完成，通过 PR 合并回 `main`
2. 审计日志全部由 Django 信号驱动，视图层无手动 `AuditLog.objects.create()`（软删除除外，题目允许日志保留）
3. 浏览量、附件下载数均使用 `F()` 做数据库原子更新，避免并发丢失计数
4. 用户密码使用 Django 内置哈希存储，不存储明文密码
5. 代码遵循 PEP8，`requirements.txt` 包含 Pillow
