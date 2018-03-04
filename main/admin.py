from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Tag, MosaicPicture, MosaicItem, MosaicSite, GeneralSettings


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
    list_display = ('site_id', 'mosaic', 'is_cover', 'image_tag', 'negative_id')

    # fields = ('image_tag',)
    # readonly_fields = ('image_tag',)
    def site_id(self, obj):
        return "{}".format(obj.mosaic.mosaic_site.site_id)

    site_id.short_description = _('Site ID')


try:
    from .solo_admin import *
except ImportError:
    pass

admin.site.register(Tag)
admin.site.register(MosaicSite, MosaicSiteAdmin)
admin.site.register(MosaicItem, MosaicItemAdmin)
admin.site.register(MosaicPicture, PictureAdmin)
admin.site.register(GeneralSettings, SingletonModelAdmin)
