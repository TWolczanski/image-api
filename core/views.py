from rest_framework import viewsets, mixins
from . import models, serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from PIL import Image
from io import BytesIO
from django.http import FileResponse


class ImageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.ImageSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Image.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        if Image.open(serializer.validated_data["file"]).format not in ["PNG", "JPEG"]:
            raise ValidationError({"file": "Unsupported image format. Only PNG and JPEG files are supported"})
        user = self.request.user
        image = serializer.save(owner=user)
        for size in user.tier.thumbnail_sizes.all():
            models.ImageLink.objects.create(image=image, size=size)
        if user.tier.links_to_original_images_allowed:
            models.ImageLink.objects.create(image=image)


class ImageLinkViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.ImageLinkSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.ImageLink.objects.filter(image__owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        image = serializer.validated_data["image"]
        if image.owner != user:
            raise PermissionDenied("You are not the owner of the image")
        if not user.tier.expiring_links_allowed:
            raise PermissionDenied("Your account tier does not allow creating expiring links to images")
        return super().perform_create(serializer)

    def retrieve(self, request, *args, **kwargs):
        link = self.get_object()
        image = Image.open(link.image.file)
        if link.size:
            height = link.size.height
            width = round(image.width / image.height * height)
            image.thumbnail((width, height))
        buffer = BytesIO()
        image.save(buffer, image.format)
        buffer.seek(0)
        return FileResponse(buffer, filename=f"{link.pk}.{image.format.lower()}")