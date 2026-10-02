from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import Article, AuditLog


@receiver(pre_save, sender=Article)
def article_pre_save_cache_old(sender, instance, **kwargs):
    """保存前把数据库中的旧对象缓存到实例上，供 post_save 对比差异。

    原因：post_save 在保存完成之后才触发，此时数据库已写入新值，
    若再 get() 读到的已是新值，无法得到 old/new 差异。
    因此必须在 pre_save（保存前，数据库仍是旧值）时缓存旧对象。
    """
    if instance.pk:
        try:
            instance._old_article = Article.objects.get(pk=instance.pk)
        except Article.DoesNotExist:
            instance._old_article = None
    else:
        instance._old_article = None


@receiver(post_save, sender=Article)
def article_post_save_handler(sender, instance, created, **kwargs):
    """文章创建 / 更新后触发，自动生成审计日志。

    1. created=True -> 新建文章，记录 create；
    2. 状态变更       -> 依据新状态记录 publish / archive；
    3. 其他更新       -> 记录 update（diff 带字段级 old/new 变更摘要）。
    """
    if created:
        AuditLog.objects.create(
            operation="create",
            article=instance,
            operator=instance.author,
            diff={"title": instance.title, "status": instance.status},
        )
        return

    old_obj = getattr(instance, "_old_article", None)
    diff = {}
    if old_obj is not None:
        if old_obj.status != instance.status:
            diff["status"] = {"old": old_obj.status, "new": instance.status}
        if old_obj.title != instance.title:
            diff["title"] = {"old": old_obj.title, "new": instance.title}

    if instance.status == "published":
        op_type = "publish"
    elif instance.status == "archived":
        op_type = "archive"
    else:
        op_type = "update"

    AuditLog.objects.create(
        operation=op_type,
        article=instance,
        operator=instance.author,
        diff=diff,
    )


@receiver(pre_delete, sender=Article)
def article_pre_delete_handler(sender, instance, **kwargs):
    """文章被物理删除（调用 delete()）之前触发，记录 delete 审计日志。"""
    AuditLog.objects.create(
        operation="delete",
        article=instance,
        operator=instance.author,
        diff={"title": instance.title},
    )
