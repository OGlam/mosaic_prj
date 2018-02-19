import os
from uuid import uuid4

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import get_valid_filename
from django.utils.translation import ugettext_lazy as _

from main.solo_models import SingletonModel


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


class ArchaeologicalContext(object):
    CHURCH = _('Church')
    SYNAGOGUE = _('Synagogue')
    PUBLIC_BUILDING = _('Public building')
    PRIVATE_BUILDING = _('Private building')

    CHOICES = (
        ('church', CHURCH),
        ('synagogue', SYNAGOGUE),
        ('public', PUBLIC_BUILDING),
        ('private', PRIVATE_BUILDING),
    )


class Tag(models.Model):
    tag_he = models.CharField(max_length=100)
    tag_en = models.CharField(max_length=100)
    featured = models.BooleanField(_('Is featured?'), default=True)

    def __str__(self):
        return self.tag_he if settings.LANGUAGE_CODE == 'he' else self.tag_en

    def get_sites(self):
        return MosaicSite.objects.filter(id__in=[x.mosaic_site_id for x in self.mosaic_items.all().distinct()])


class MosaicSite(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    site_id = models.CharField(_('Site ID'), max_length=200)  # MOTSA (3357/12)
    title_he = models.CharField(_('Title hebrew'), max_length=200)  # Display name
    title_en = models.CharField(_('Title english'), max_length=200)  # Display name
    origin_he = models.CharField(_('Origin hebrew'), max_length=100)  # MOTSA (address)
    origin_en = models.CharField(_('Origin english'), max_length=100)  # MOTSA (address)
    story_he = models.TextField(_('Story hebrew'), blank=True)
    story_en = models.TextField(_('Story english'), blank=True)
    archaeological_context = models.CharField(_('Archaeological context'), max_length=50, blank=True,
                                              choices=ArchaeologicalContext.CHOICES)
    period = models.CharField(_('Period'), max_length=50, blank=True, choices=Periods.CHOICES)
    video_id = models.CharField(_('Youtube video ID'), max_length=50, blank=True)
    comments = models.TextField(_('Comments'), blank=True)
    featured = models.BooleanField(_('Is featured?'), default=False)
    latitude = models.FloatField(_('Latitude'), blank=True, null=True)
    longitude = models.FloatField(_('Longitude'), blank=True, null=True)

    def __str__(self):
        return u'[{}] {}'.format(self.site_id, self.title_he if settings.LANGUAGE_CODE == 'he' else self.title_en)

    def get_site_cover_image(self):
        return MosaicPicture.objects.filter(mosaic__mosaic_site=self, is_cover=True).order_by('?')

    def get_site_pictures(self):
        return MosaicPicture.objects.filter(mosaic__mosaic_site_id=self.id).order_by('mosaic')

    def get_site_cover_image_url(self):
        if self.get_site_cover_image():
            return self.get_site_cover_image()[0].picture.url
        return "{}images/empty-image.png".format(settings.STATIC_URL)


class MosaicItem(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    mosaic_site = models.ForeignKey(MosaicSite, verbose_name=_('Mosaic site'), on_delete=models.CASCADE,
                                    related_name='items')
    misp_rashut = models.CharField(verbose_name=_('Rashut number'), max_length=200)
    description_he = models.TextField(_('Description hebrew'), blank=True)
    description_en = models.TextField(_('Description english'), blank=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'), blank=True, related_name='mosaic_items')
    length = models.DecimalField(_('Length'), max_digits=10, decimal_places=4, blank=True, null=True)
    width = models.DecimalField(_('Width'), max_digits=10, decimal_places=4, blank=True, null=True)
    area = models.DecimalField(_('Area'), max_digits=15, decimal_places=2, blank=True, null=True)
    rishayon = models.CharField(_('Rishayon'), max_length=50, blank=True)
    materials = ArrayField(models.CharField(_('Material'), max_length=50, choices=Materials.CHOICES),
                           blank=True, null=True)
    year = models.CharField(_('Year'), max_length=200, blank=True)  # RISHAYON (/1972)
    displayed_at = models.CharField(_('Displayed at'), max_length=200, blank=True)
    bibliography_he = models.TextField(_('Bibliography hebrew'), blank=True)
    bibliography_en = models.TextField(_('Bibliography english'), blank=True)

    def __str__(self):
        return self.misp_rashut

    def get_materials(self):
        return ",".join(self.materials)

    def get_highest_cover(self):
        res = self.pictures.filter(is_cover=True).order_by('order_priority').first()
        if res:
            return res.picture.url
        return '{}images/empty-image.png'.format(settings.STATIC_URL)


class MosaicPicture(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    mosaic = models.ForeignKey(MosaicItem, verbose_name=_('Mosaic'), on_delete=models.CASCADE, related_name='pictures')
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'), blank=True, related_name='mosaic_pictures')
    is_cover = models.BooleanField(_('Cover image'), default=False)
    order_priority = models.IntegerField(_('Order priority'), default=100)
    picture = models.ImageField(_('Picture'), upload_to=mosaic_dir)
    negative_id = models.CharField(_('Negative ID'), max_length=50)
    photographer_name_he = models.CharField(_('Photographer name hebrew'), max_length=200, blank=True)
    photographer_name_en = models.CharField(_('Photographer name english'), max_length=200, blank=True)
    taken_at = models.CharField(_('Taken at'), max_length=200, blank=True)
    picture_type = models.CharField(_('Picture type'), max_length=50, choices=PictureType.CHOICES, blank=True)
    taken_date = models.DateField(_('Taken date'), blank=True, null=True)
    comments_he = models.TextField(_('Comments hebrew'), blank=True)
    comments_en = models.TextField(_('Comments english'), blank=True)

    def __str__(self):
        return self.negative_id

    def get_image(self):
        if self.picture:
            return self.picture.url
        return '{}images/empty-image.png'.format(settings.STATIC_URL)

    def image_tag(self):
        if self.picture:
            return mark_safe('<img src="{}" height="100%" width="auto" />'.format(self.picture.url))
        else:
            return '-'

    image_tag.short_description = 'Image'


class GeneralSettings(SingletonModel):
    logo = models.FileField(_('Logo'), blank=True, null=True)
    site_name_he = models.CharField(verbose_name=_('Site name Hebrew'), max_length=255, blank=True)
    site_name_en = models.CharField(verbose_name=_('Site name English'), max_length=255, blank=True)
    admin_email_from = models.CharField(verbose_name=_('Admin email from'), max_length=255, blank=True)
    admin_email_to = models.EmailField(verbose_name=_('Admin email to'), max_length=255, blank=True)
    about_he = models.TextField(verbose_name=_('About Hebrew'), blank=True, null=True)
    about_en = models.TextField(verbose_name=_('About English'), blank=True, null=True)

    def __str__(self):
        return u"{}".format(_('General settings'))

    class Meta:
        verbose_name = _("General settings")

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return ''
