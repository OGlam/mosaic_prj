from django.contrib import admin
from .models import Tag, MosaicPicture, MosaicItem, MosaicSite


class PictureInline(admin.TabularInline):
    model = MosaicPicture
    extra = 1
    list_display = ('image_tag', 'product',)
    readonly_fields = ('image_tag',)


class MosaicItemAdmin(admin.ModelAdmin):
    inlines = [PictureInline]


class PictureAdmin(admin.ModelAdmin):
    fields = ('image_tag',)
    readonly_fields = ('image_tag',)


admin.site.register(Tag)
admin.site.register(MosaicSite)
admin.site.register(MosaicItem, MosaicItemAdmin)
admin.site.register(MosaicPicture, PictureAdmin)
