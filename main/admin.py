from django.contrib import admin

# Register your models here.
from .models import Mosaic, Tags, MosaicPicture


class PictureInLine (admin.TabularInline):
    model = MosaicPicture
    extra = 1


class MosaicAdmin (admin.ModelAdmin):
    inlines = [PictureInLine]


admin.site.register(Tags)
admin.site.register(Mosaic, MosaicAdmin)
admin.site.register(MosaicPicture)

