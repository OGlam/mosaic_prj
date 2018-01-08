from django.contrib import admin

from main.get_data import get_data
from .models import Tag, MosaicPicture, MosaicItem, MosaicSite


class MosaicSiteAdmin(admin.ModelAdmin):
    list_display = ('site_id', 'title_he', 'title_en', 'origin_he', 'origin_en')
    list_display_links = ('site_id', 'title_he', 'title_en', 'origin_he', 'origin_en')


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
admin.site.register(MosaicSite, MosaicSiteAdmin)
admin.site.register(MosaicItem, MosaicItemAdmin)
admin.site.register(MosaicPicture, PictureAdmin)

