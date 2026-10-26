from django.urls import path
from .views import preview, script, learn, BlackLinePredictionAPI, ReferencePredictionSaveAPI

urlpatterns = [
    path("predictions/save", ReferencePredictionSaveAPI.as_view({"post": "create"})),
    path("learn", learn),
    path("preview", preview), path("panel.js", script),
    path("predictions/<int:pk>", BlackLinePredictionAPI.as_view({"delete": "destroy"})),
]
