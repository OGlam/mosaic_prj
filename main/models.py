from django.db import models

# Create your models here.
from django.utils.safestring import mark_safe
from django.utils.text import get_valid_filename


class Tags(models.Model):
    tag = models.CharField(max_length=20)

    def __str__(self):
        return self.tag


class Mosaic(models.Model):
    # top_picture = models.ForeignKey(MosaicPicture, blank=True)
    title = models.CharField(max_length=200)
    origin = models.CharField(max_length=100)
    date = models.DateField()
    story = models.TextField(blank = True)
    # media =
    iaa_id = models.CharField(max_length=50)
    iaa_permission_code = models.CharField(max_length=50)
    place_name = models.CharField(blank = True, max_length=100)
    # gps_longitude
    # gps_latitude
    address = models.CharField(blank = True, max_length=200)
    period = models.CharField(max_length=50)
    displayed_at = models.CharField(blank = True, max_length=200)
    tags = models.ManyToManyField(Tags)
    material = models.CharField(max_length=50)
    dimen_length = models.DecimalField(max_digits=10, decimal_places=4)
    dimen_width = models.DecimalField(max_digits=10, decimal_places=4)
    dimen_area = models.DecimalField(max_digits=15, decimal_places=2)
    comments = models.TextField(blank=True)
    bibliography = models.TextField(blank=True)
    publications = models.TextField(blank=True)

    # pictures

    def __str__(self):
        return self.title


def mosaic_dir(instance, filename):
    import unicodedata
    value = get_valid_filename(instance.mosaic.origin)
    return 'mosaic_pictures/{0}_{1}/{2}'.format(instance.mosaic.id,value, filename)


class MosaicPicture(models.Model):
    mosaic = models.ForeignKey(Mosaic, on_delete=models.CASCADE)
    order_priority = models.IntegerField (default=100)
    picture = models.ImageField(upload_to=mosaic_dir)
    negative_id = models.CharField(max_length=50)
    photographer_name = models.CharField(max_length=100)
    taken_at = models.CharField(blank = True, max_length=100)
    picture_type = models.CharField(max_length=50)
    taken_date = models.DateField()
    comments = models.TextField(blank = True)

    def image_tag(self):
        if self.picture:
            return mark_safe('<img src="/media/%s" width="150" height="150" />' % self.picture)
        else:
            return '-'
    image_tag.short_description = 'Image'

    def __str__(self):
        return self.negative_id