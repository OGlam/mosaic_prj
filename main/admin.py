from django.contrib import admin

# Register your models here.
from .models import Mosaic, Tags, MosaicPicture


class PictureInLine (admin.TabularInline):
    model = MosaicPicture
    extra = 1
    list_display = ('image_tag', 'product',)
    readonly_fields = ('image_tag',)


class MosaicAdmin (admin.ModelAdmin):
    inlines = [PictureInLine]


class PictureAdmin (admin.ModelAdmin):
    fields = ('image_tag',)
    readonly_fields = ('image_tag',)


admin.site.register(Tags)
admin.site.register(Mosaic, MosaicAdmin)
admin.site.register(MosaicPicture, PictureAdmin)

