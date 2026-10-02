from django.contrib import admin
from .models import Article, Attachment, AuditLog


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "views", "is_deleted", "created_at")
    list_filter = ("status", "is_deleted")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("file_name", "article", "downloads", "upload_time")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("operation", "article", "operator", "timestamp")
    list_filter = ("operation",)
