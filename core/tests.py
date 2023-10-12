from rest_framework import status
from rest_framework.test import APITestCase
from . import models
from rest_framework.authtoken.models import Token
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta


class CoreTestCase(APITestCase):
    fixtures = ["initial"]

    def setUp(self):
        self.user_basic = models.User.objects.create(
            username="user_basic",
            password="GbzqGXugtf4KHjn",
            email="user@basic.com",
            tier=models.Tier.objects.get(name="Basic")
        )
        self.user_premium = models.User.objects.create(
            username="user_premium",
            password="XqFrW6LXCZsXYuF",
            email="user@premium.com",
            tier=models.Tier.objects.get(name="Premium")
        )
        self.user_enterprise = models.User.objects.create(
            username="user_enterprise",
            password="4Xagai2ylklAwLj",
            email="user@enterprise.com",
            tier=models.Tier.objects.get(name="Enterprise")
        )
        self.token_basic = Token.objects.create(user=self.user_basic)
        self.token_premium = Token.objects.create(user=self.user_premium)
        self.token_enterprise = Token.objects.create(user=self.user_enterprise)
    
    def create_image(self, width, height, format):
        image = Image.new("RGB", (width, height))
        buffer = BytesIO()
        image.save(buffer, format)
        buffer.seek(0)
        return SimpleUploadedFile("image.png", buffer.getvalue(), "image/png")

    def test_basic_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_basic.key)

        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Image.objects.count(), 1)
        self.assertEqual(models.ImageLink.objects.count(), 1)
        link = models.ImageLink.objects.get()
        self.assertEqual(link.size.height, 200)

        response = self.client.get("/images/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(f"/images/links/{link.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        buffer = BytesIO(b"".join(response.streaming_content))
        image = Image.open(buffer)
        self.assertEqual(image.format, "PNG")
        self.assertEqual(image.height, 200)

        data = {"image": models.Image.objects.get().pk, "duration": timedelta(seconds=300)}
        response = self.client.post(f"/images/links/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_premium_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_premium.key)

        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Image.objects.count(), 1)
        self.assertEqual(models.ImageLink.objects.count(), 3)
        links = models.ImageLink.objects.all()
        self.assertEqual({link.size.height if link.size else None for link in links}, {200, 400, None})

        response = self.client.get("/images/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for link in links:
            response = self.client.get(f"/images/links/{link.pk}/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            buffer = BytesIO(b"".join(response.streaming_content))
            image = Image.open(buffer)
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.height, link.size.height if link.size else 600)

        data = {"image": models.Image.objects.get().pk, "duration": timedelta(seconds=300)}
        response = self.client.post(f"/images/links/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_enterprise_user(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_enterprise.key)

        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Image.objects.count(), 1)
        self.assertEqual(models.ImageLink.objects.count(), 3)
        links = models.ImageLink.objects.all()
        self.assertEqual({link.size.height if link.size else None for link in links}, {200, 400, None})

        response = self.client.get("/images/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for link in links:
            response = self.client.get(f"/images/links/{link.pk}/")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            buffer = BytesIO(b"".join(response.streaming_content))
            image = Image.open(buffer)
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.height, link.size.height if link.size else 600)

        data = {"image": models.Image.objects.get().pk, "duration": timedelta(seconds=300)}
        response = self.client.post(f"/images/links/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.ImageLink.objects.count(), 4)
        self.assertEqual(models.ImageLink.objects.filter(size=None).count(), 2)
    
    def test_image_format(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_basic.key)

        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post("/images/", {"file": self.create_image(800, 600, "JPEG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post("/images/", {"file": self.create_image(800, 600, "GIF")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.post("/images/", {"file": self.create_image(800, 600, "BMP")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_access_others_image(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_basic.key)

        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(models.Image.objects.count(), 1)
        self.assertEqual(models.ImageLink.objects.count(), 1)
        image = models.Image.objects.get()
        link = models.ImageLink.objects.get()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token_enterprise.key)

        response = self.client.get(f"/images/links/{link.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        data = {"image": image.pk, "duration": timedelta(seconds=300)}
        response = self.client.post(f"/images/links/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_auth_required(self):
        response = self.client.post("/images/", {"file": self.create_image(800, 600, "PNG")}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.get("/images/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)