from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models import F, Q
from datetime import datetime


class ImageSize(models.Model):
    height = models.IntegerField()

    def __str__(self):
        return str(self.height)


class Tier(models.Model):
    name = models.CharField(max_length=30)
    thumbnail_sizes = models.ManyToManyField(ImageSize)
    links_to_original_images_allowed = models.BooleanField(default=False)
    expiring_links_allowed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    tier = models.ForeignKey(Tier, blank=True, null=True, on_delete=models.SET_NULL)


class Image(models.Model):
    file = models.ImageField(upload_to="core/images")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")

    def __str__(self):
        return str(self.file)


class ImagePreviewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            Q(duration__isnull=True) |
            Q(duration__gte=datetime.now() - F("created_at"))
        )

class ImagePreview(models.Model):
    objects = ImagePreviewManager()
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="previews")
    size = models.ForeignKey(ImageSize, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(blank=True, null=True)

    def __str__(self):
        return str(self.id)