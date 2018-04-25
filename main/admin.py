from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Tag, MosaicPicture, MosaicItem, MosaicSite, GeneralSettings, TagCategory


class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('tag_category_he', 'tag_category_en')
    list_display_links = ('tag_category_he', 'tag_category_en')


class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_he', 'tag_en', 'tag_category', 'featured')
    list_display_links = ('tag_he', 'tag_en', 'tag_category', 'featured')

class MosaicSiteAdmin(admin.ModelAdmin):
    list_display = ('site_id', 'title_he', 'title_en', 'origin_he', 'origin_en')
    list_display_links = ('site_id', 'title_he', 'title_en', 'origin_he', 'origin_en')


class PictureInline(admin.StackedInline):
    model = MosaicPicture
    extra = 1
    list_display = ('image_tag', 'product',)
    readonly_fields = ('image_tag',)


class MosaicItemAdmin(admin.ModelAdmin):
    inlines = [PictureInline]
    list_display = (
        'id',
        'mosaic_site',
        'misp_rashut',
        'description_he',
        'description_en',
    )


class PictureAdmin(admin.ModelAdmin):
    list_display = (
        'site_id',
        'mosaic',
        'is_cover',
        'taken_date',
        'taken_at',
        'image_tag',
        'picture_type',
        'negative_id',
        'photographer_name_he',
        'photographer_name_en',
        'comments_he',
        'comments_en',
    )

    # fields = ('image_tag',)
    # readonly_fields = ('image_tag',)
    def site_id(self, obj):
        return "{}".format(obj.mosaic.mosaic_site.site_id)

    site_id.short_description = _('Site ID')


try:
    from .solo_admin import *
except ImportError:
    pass

admin.site.register(TagCategory, TagCategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(MosaicSite, MosaicSiteAdmin)
admin.site.register(MosaicItem, MosaicItemAdmin)
admin.site.register(MosaicPicture, PictureAdmin)
admin.site.register(GeneralSettings, SingletonModelAdmin)
