from django.contrib import admin
from .models import Mosaic, Tag, MosaicPicture


class PictureInline(admin.TabularInline):
    model = MosaicPicture
    extra = 1
    list_display = ('image_tag', 'product',)
    readonly_fields = ('image_tag',)


class MosaicAdmin(admin.ModelAdmin):
    inlines = [PictureInline]


class PictureAdmin(admin.ModelAdmin):
    fields = ('image_tag',)
    readonly_fields = ('image_tag',)


admin.site.register(Tag)
admin.site.register(Mosaic, MosaicAdmin)
admin.site.register(MosaicPicture, PictureAdmin)
