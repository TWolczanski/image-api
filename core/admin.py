from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ImageSize, Tier, User, Image, ImagePreview

admin.site.register(ImageSize)
admin.site.register(Tier)
UserAdmin.list_display += ("tier",)
UserAdmin.fieldsets += (("tier", {"fields": ("tier",)}),)
admin.site.register(User, UserAdmin)
admin.site.register(Image)
admin.site.register(ImagePreview)
