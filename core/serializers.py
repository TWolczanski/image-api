from . import models
from rest_framework import serializers
from datetime import timedelta


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Image
        fields = ["id", "file", "links"]
        read_only_fields = ["id", "links"]


class ImageLinkSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.PrimaryKeyRelatedField(queryset=models.Image.objects.all(), write_only=True)
    duration = serializers.DurationField(min_value=timedelta(seconds=300), max_value=timedelta(seconds=30000), write_only=True)

    class Meta:
        model = models.ImageLink
        fields = ["url", "image", "duration"]