"""集成自测脚本：验证信号审计、F表达式浏览量、软删除、附件计数、统计。
用法: py manage.py shell -c "exec(open('selftest.py', encoding='utf-8').read())"
"""
from django.contrib.auth.models import User
from django.db.models import F, Count, Sum
from article.models import Article, Attachment, AuditLog

print("=== 自测开始 ===")

# 1) 清理 + 造用户
AuditLog.objects.all().delete()
Attachment.objects.all().delete()
Article.objects.all().delete()
u, _ = User.objects.get_or_create(username="tester")
u.set_password("testpass123")
u.save()
print("1) 用户就绪:", u.username)

# 2) 创建文章 -> 触发 post_save(created) 生成 create 审计
a = Article.objects.create(title="测试文章", content="正文内容", author=u, status="draft")
logs = AuditLog.objects.filter(article=a)
ops = set(logs.values_list("operation", flat=True))
print("2) 创建后审计日志 =", ops, "| 数量 =", logs.count())
assert logs.count() == 1 and "create" in ops, "创建信号失败"

# 3) 状态变更 draft->published -> 生成 publish，diff 记录 old/new
a.status = "published"
a.save()
logs = AuditLog.objects.filter(article=a)
ops = list(logs.values_list("operation", flat=True))
print("3) 状态变更后审计 =", ops)
assert "publish" in ops, "状态变更信号失败"
pub = logs.get(operation="publish")
print("   publish diff =", pub.diff)
assert pub.diff.get("status") == {"old": "draft", "new": "published"}, "diff 未记录 old/new"

# 4) F 表达式浏览量原子自增
for _ in range(5):
    Article.objects.filter(pk=a.pk).update(views=F("views") + 1)
a.refresh_from_db()
print("4) 浏览量(F自增5次) =", a.views)
assert a.views == 5, "浏览量F自增失败"

# 5) 附件上传 + 下载计数 F 自增
att = Attachment.objects.create(file_name="readme.txt", file="attachments/readme.txt", article=a)
for _ in range(3):
    Attachment.objects.filter(pk=att.pk).update(downloads=F("downloads") + 1)
att.refresh_from_db()
print("5) 附件下载计数(F自增3次) =", att.downloads)
assert att.downloads == 3, "附件下载计数失败"

# 6) 软删除
a.is_deleted = True
a.save()
print("6) 软删除后 is_deleted =", a.is_deleted, "| 物理记录仍在 id =", a.pk)
assert a.is_deleted and Article.objects.filter(pk=a.pk).exists()

# 7) 统计聚合
tot = Article.objects.filter(is_deleted=False).count()
v = Article.objects.filter(is_deleted=False).aggregate(s=Sum("views"))["s"] or 0
print("7) 未删除文章数 =", tot, "| 未删除总浏览量 =", v)

# 8) 物理删除 -> 触发 pre_delete 生成 delete 审计
a2 = Article.objects.create(title="待物理删除", content="x", author=u)
a2.delete()
del_log = AuditLog.objects.filter(operation="delete").order_by("-timestamp").first()
print("8) 物理删除后 delete 审计 =", del_log.operation if del_log else None)
assert del_log is not None and del_log.operation == "delete", "物理删除信号失败"

print("=== 自测通过 ===")
