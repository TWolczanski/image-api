from django.contrib import admin
from django.urls import path
from rest_framework import routers
from core import views

router = routers.DefaultRouter()
router.register(r"images", views.ImageViewSet, basename="image")
router.register(r"images/previews", views.ImagePreviewViewSet, basename="imagepreview")

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += router.urls
