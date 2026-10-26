from django.urls import include, path
from .merge_views import preview, script, MergeAnnotationAPI

urlpatterns = [
    path("reference-segmenter/", include("reference_segmenter.urls")),
    path("mask-merge/tasks/<int:pk>/annotations", MergeAnnotationAPI.as_view()),
    path("mask-merge/preview", preview),
    path("mask-merge/panel.js", script),
    path("", include("mask_cleanup.urls")),
]
