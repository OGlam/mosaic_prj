import os
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import get_valid_filename
from django.utils.translation import ugettext as _


def mosaic_dir(instance, filename):
    # name, ext = os.path.splitext(filename)
    # num = instance.pk if instance.pk else uuid4().hex[:15]
    # return '{0}/pic_{1}{2}'.format(instance.__class__.__name__.lower(), num, ext.lower())
    value = get_valid_filename(instance.mosaic.mosaic_site)
    return 'mosaics/{}/{}'.format(value, filename)


class Periods(object):
    BYZANTINE = _('Byzantine')

    CHOICES = (
        ('byzantine', BYZANTINE),
        # todo: increase list.
    )


class Materials(object):
    STONE = _('Stone')
    GLASS = _('Glass')

    CHOICES = (
        ('stone', STONE),
        ('glass', GLASS),
        # todo: increase list.
    )


class PictureType(object):
    EXCAVATION = _('Excavation')
    POST_EXCAVATION = _('Post Excavation')
    PRESERVATION = _('Preservation')

    CHOICES = (
        ('excavation', EXCAVATION),
        ('post_excavation', POST_EXCAVATION),
        ('preservation', PRESERVATION),
        # todo: increase list.
    )


class ArcheologicalContext(object):
    CHURCH = _('Church')
    SYNAGOGUE = _('Synagogue')
    PUBLIC_BUILDING = _('Public building')

    CHOICES = (
        ('church', CHURCH),
        ('synagogue', SYNAGOGUE),
        ('public', PUBLIC_BUILDING),
    )


class Tag(models.Model):
    tag_he = models.CharField(max_length=100)
    tag_en = models.CharField(max_length=100)

    def __str__(self):
        return self.tag_he if settings.LANGUAGE_CODE == 'he' else self.tag_en

    def get_lang_tag(self):
        return self.tag_he if settings.LANGUAGE_CODE == 'he' else self.tag_en


class MosaicSite(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    site_id = models.CharField(_('Site ID'), max_length=200)  # MOTSA (3357/12)
    title = models.CharField(_('Title'), max_length=200)  # Display name
    origin = models.CharField(_('Origin'), max_length=100)  # MOTSA (address)
    story = models.TextField(_('Story'), blank=True)
    archeological_context = models.CharField(_('Archeological context'), max_length=50, blank=True,
                                             choices=ArcheologicalContext.CHOICES)
    period = models.CharField(_('Period'), max_length=50, blank=True, choices=Periods.CHOICES)
    video_id = models.CharField(_('Youtube video ID'), max_length=50, blank=True)
    comments = models.TextField(_('Comments'), blank=True)
    featured = models.BooleanField(_('Is featured?'), default=False)
    latitude = models.FloatField(_('Latitude'), blank=True, null=True)
    longitude = models.FloatField(_('Longitude'), blank=True, null=True)

    def __str__(self):
        return u'[{}] {}'.format(self.site_id, self.title)

    def get_site_cover_image(self):
        return MosaicPicture.objects.filter(mosaic__mosaic_site=self, is_cover=True).order_by('?')


class MosaicItem(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    mosaic_site = models.ForeignKey(MosaicSite, verbose_name=_('Mosaic site'), on_delete=models.CASCADE,
                                    related_name='items')
    misp_rashut = models.CharField(verbose_name=_('Rashut number'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'), blank=True, related_name='mosaic_items')
    length = models.DecimalField(_('Length'), max_digits=10, decimal_places=4, blank=True, null=True)
    width = models.DecimalField(_('Width'), max_digits=10, decimal_places=4, blank=True, null=True)
    area = models.DecimalField(_('Area'), max_digits=15, decimal_places=2, blank=True, null=True)
    rishayon = models.CharField(_('Rishayon'), max_length=50)
    materials = ArrayField(models.CharField(_('Material'), max_length=50, choices=Materials.CHOICES),
                           blank=True, null=True)
    year = models.CharField(_('Year'), max_length=200, blank=True)  # RISHAYON (/1972)
    displayed_at = models.CharField(_('Displayed at'), max_length=200, blank=True)
    bibliography = models.TextField(_('Bibliography'), blank=True)

    def __str__(self):
        return self.misp_rashut

    def get_all_pictures_by_position(self):
        return self.pictures.order_by('-order_priority')


class MosaicPicture(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    mosaic = models.ForeignKey(MosaicItem, verbose_name=_('Mosaic'), on_delete=models.CASCADE, related_name='pictures')
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'), blank=True, related_name='mosaic_pictures')
    is_cover = models.BooleanField(_('Cover image'), default=False)
    order_priority = models.IntegerField(_('Order priority'), default=100)
    picture = models.ImageField(_('Picture'), upload_to=mosaic_dir)
    negative_id = models.CharField(_('Negative ID'), max_length=50)
    photographer_name = models.CharField(_('Photographer name'), max_length=200, blank=True)
    taken_at = models.CharField(_('Taken at'), max_length=200, blank=True)
    picture_type = models.CharField(_('Picture type'), max_length=50, choices=PictureType.CHOICES, blank=True)
    taken_date = models.DateField(_('Taken date'), blank=True, null=True)
    comments = models.TextField(_('Comments'), blank=True)

    def __str__(self):
        return self.negative_id

    def image_tag(self):
        if self.picture:
            return mark_safe('<img src="{}" height="100%" width="auto" />'.format(self.picture.url))
        else:
            return '-'

    image_tag.short_description = 'Image'
