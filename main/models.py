import os
from uuid import uuid4
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import get_valid_filename
from django.utils.translation import ugettext as _


def mosaic_dir(instance, filename):
    # name, ext = os.path.splitext(filename)
    # num = instance.pk if instance.pk else uuid4().hex[:15]
    # return '{0}/pic_{1}{2}'.format(instance.__class__.__name__.lower(), num, ext.lower())
    value = get_valid_filename(instance.mosaic.origin)
    return 'mosaics/{0}_{1}/{2}'.format(instance.mosaic.id, value, filename)


class Tag(models.Model):
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.tag


class Mosaic(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    origin = models.CharField(_('Origin'), max_length=100)
    date = models.DateField()
    story = models.TextField(_('Story'), null=True, blank=True)
    iaa_id = models.CharField(_('IAA ID'), max_length=50)
    iaa_permission_code = models.CharField(_('IAA permission code'), max_length=50)
    place_name = models.CharField(_('Place name'), max_length=100, blank=True, null=True)
    # gps_longitude
    # gps_latitude
    address = models.CharField(_('Address'), max_length=200, blank=True, null=True)
    period = models.CharField(_('Period'), max_length=50)
    displayed_at = models.CharField(_('Displayed at'), max_length=200, blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name=_('Tags'), blank=True, related_name='mosaics')
    material = models.CharField(_('Material'), max_length=50)
    dimen_length = models.DecimalField(max_digits=10, decimal_places=4)
    dimen_width = models.DecimalField(max_digits=10, decimal_places=4)
    dimen_area = models.DecimalField(max_digits=15, decimal_places=2)
    comments = models.TextField(_('Comments'), blank=True, null=True)
    bibliography = models.TextField(_('Bibliography'), blank=True, null=True)
    publications = models.TextField(_('Publications'), blank=True, null=True)

    def __str__(self):
        return self.title


class MosaicPicture(models.Model):
    mosaic = models.ForeignKey(Mosaic, verbose_name=_('Mosaic'), on_delete=models.CASCADE, related_name='pictures')
    order_priority = models.IntegerField(default=100)
    picture = models.ImageField(_('Picture'), upload_to=mosaic_dir)
    negative_id = models.CharField(_('Negative ID'), max_length=50)
    photographer_name = models.CharField(_('Photographer name'), max_length=100, blank=True, null=True)
    taken_at = models.CharField(_('Taken at'), max_length=200, blank=True, null=True)
    picture_type = models.CharField(_('Picture type'), max_length=50)
    taken_date = models.DateField(_('Taken date'))
    comments = models.TextField(_('Comments'), blank=True, null=True)

    def __str__(self):
        return self.negative_id

    def image_tag(self):
        if self.picture:
            return mark_safe('<img src="{}" width="150" height="150" />'.format(self.picture.url))
        else:
            return '-'

    image_tag.short_description = 'Image'
