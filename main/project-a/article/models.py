from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


class Article(models.Model):
    """文章数据模型"""
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("published", "已发布"),
        ("archived", "已归档"),
    ]

    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="正文")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="作者",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="状态",
    )
    views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    # 加分项：软删除（标记删除，不物理删除记录）
    is_deleted = models.BooleanField(default=False, verbose_name="是否软删除")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]


class Attachment(models.Model):
    """附件数据模型"""
    file_name = models.CharField(max_length=255, verbose_name="文件名")
    file = models.FileField(upload_to="attachments/", verbose_name="文件")
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="关联文章",
    )
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    # 加分项：附件下载计数
    downloads = models.PositiveIntegerField(default=0, verbose_name="下载次数")

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = "附件"
        verbose_name_plural = "附件"
        ordering = ["-upload_time"]


class AuditLog(models.Model):
    """审计日志数据模型：记录文章操作历史"""
    OP_CHOICES = [
        ("create", "创建"),
        ("update", "更新"),
        ("publish", "发布"),
        ("archive", "归档"),
        ("delete", "删除"),
    ]

    operation = models.CharField(
        max_length=20,
        choices=OP_CHOICES,
        verbose_name="操作类型",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="关联文章",
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="操作人",
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    diff = JSONField(default=dict, verbose_name="变更摘要")

    def __str__(self):
        return f"{self.operation} - {self.timestamp}"

    class Meta:
        verbose_name = "审计日志"
        verbose_name_plural = "审计日志"
        ordering = ["-timestamp"]
