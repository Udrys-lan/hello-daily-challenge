from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("articles/", views.article_list, name="article_list"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("attachment/upload/<int:article_id>/", views.attachment_upload, name="att_upload"),
    path("attachment/delete/<int:att_id>/", views.attachment_delete, name="att_delete"),
    path("attachment/download/<int:att_id>/", views.attachment_download, name="att_download"),
    path("article/soft-delete/<int:pk>/", views.article_soft_delete, name="soft_delete"),
    path("stats/", views.stats_view, name="stats"),
]
