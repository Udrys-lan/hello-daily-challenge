from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, Count, Sum
from django.contrib import messages
from django.http import FileResponse
from .models import Article, Attachment, AuditLog


def article_detail(request, pk):
    """文章详情页：浏览量原子自增，展示附件列表与审计日志。"""
    article = get_object_or_404(Article, pk=pk, is_deleted=False)

    # ===================== 并发安全浏览量 =====================
    # 【错误写法】 article.views += 1; article.save()
    # 并发场景下，多个请求会读到同一个旧 views 值，在 Python 内存各自 +1 后再 save，
    # 后写回者覆盖前写回者，造成计数丢失（丢失更新 / lost update）。
    # 正确做法：使用 F 表达式，把 views+1 的计算直接交给数据库在 SQL 层执行，
    # 数据库对该行加锁后原子更新，从而避免竞态条件。
    Article.objects.filter(pk=article.pk).update(views=F("views") + 1)
    # 重新从数据库读取最新浏览量，用于页面渲染
    article.refresh_from_db()

    attachments = article.attachments.all()
    audit_logs = article.audit_logs.all().order_by("-timestamp")
    return render(request, "article/article_detail.html", {
        "article": article,
        "attachments": attachments,
        "audit_logs": audit_logs,
    })


@login_required
def attachment_upload(request, article_id):
    """上传附件：仅文章作者可为自己的文章上传，文件保存到 MEDIA_ROOT/attachments/。"""
    article = get_object_or_404(Article, pk=article_id, is_deleted=False)
    if article.author != request.user:
        messages.error(request, "只能给自己的文章上传附件")
        return redirect("article_detail", pk=article_id)

    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        Attachment.objects.create(
            file_name=f.name,
            file=f,
            article=article,
        )
        messages.success(request, "附件上传成功")
    return redirect("article_detail", pk=article_id)


@login_required
def attachment_delete(request, att_id):
    """删除附件：仅文章作者可删除自己文章的附件。"""
    att = get_object_or_404(Attachment, pk=att_id)
    if att.article.author != request.user:
        messages.error(request, "无权删除该附件")
        return redirect("article_detail", pk=att.article.pk)
    att.delete()
    messages.success(request, "附件已删除")
    return redirect("article_detail", pk=att.article.pk)


@login_required
def attachment_download(request, att_id):
    """附件下载：加分项——下载次数使用 F 表达式原子 +1，并返回文件。"""
    att = get_object_or_404(Attachment, pk=att_id)
    # 与浏览量同理：用 F 表达式做数据库层原子递增，避免并发丢计数
    Attachment.objects.filter(pk=att.pk).update(downloads=F("downloads") + 1)
    att.refresh_from_db()
    response = FileResponse(att.file.open("rb"))
    response["Content-Disposition"] = f'attachment; filename="{att.file_name}"'
    return response


# 加分项：统计页面 /stats/
def stats_view(request):
    total_articles = Article.objects.filter(is_deleted=False).count()
    total_views = (
        Article.objects.filter(is_deleted=False)
        .aggregate(total=Sum("views"))["total"] or 0
    )
    status_stats = (
        Article.objects.filter(is_deleted=False)
        .values("status")
        .annotate(cnt=Count("id"))
    )
    recent_logs = AuditLog.objects.all()[:10]
    return render(request, "article/stats.html", {
        "total_articles": total_articles,
        "total_views": total_views,
        "status_stats": status_stats,
        "recent_logs": recent_logs,
    })


@login_required
def article_soft_delete(request, pk):
    """加分项：软删除。只把 is_deleted 置为 True，不物理删除记录，
    因此 pre_delete 信号不会触发；这里手动补写一条审计日志（题目允许软删除时日志保留）。
    """
    art = get_object_or_404(Article, pk=pk)
    if art.author != request.user:
        messages.error(request, "无权删除")
        return redirect("article_detail", pk=pk)

    art.is_deleted = True
    art.save()
    # 手动记录软删除审计（保留历史痕迹）
    AuditLog.objects.create(
        operation="delete",
        article=art,
        operator=request.user,
        diff={"title": art.title, "soft_delete": True},
    )
    messages.success(request, "文章已删除（软删除）")
    return redirect("article_list")


def article_list(request):
    """文章列表：仅展示未删除文章，便于浏览与跳转详情（公开可访问）。"""
    articles = Article.objects.filter(is_deleted=False)
    return render(request, "article/article_list.html", {"articles": articles})


# 首页：重定向到文章列表
def index(request):
    return redirect("article_list")
