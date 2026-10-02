from django.apps import AppConfig


class ArticleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'article'

    def ready(self):
        # 关键：在此导入 signals，注册 post_save / pre_delete 信号。
        # 若不写这行，信号不会被加载，审计日志将无法自动生成（且无任何报错）。
        import article.signals  # noqa: F401
