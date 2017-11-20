from django.db import models

# Create your models here.
from django.db import models

# Create your models here.


class Mosaic(models.Model):
    title = models.CharField(max_length=200)
    origin = models.CharField(max_length=100)
    date = models.DateTimeField()
    story = models.TextField()
    # media =
    iaa_id = models.CharField(max_length=50)
    iaa_permission_code = models.CharField(max_length=50)
    place_name = models.CharField(max_length=100)
    # gps_longitude
    # gps_latitude
    address = models.CharField(max_length=200)
    period = models.CharField(max_length=50)
    displayed_at =  models.CharField(max_length=200)
    tags =  models.ManyToManyField(Tags)
    matriel = models.CharField(max_length=50)
    dimen_length = models.DecimalField(max_digits=10,decimal_places=2)
    dimen_width = models.DecimalField(max_digits=10,decimal_places=2)
    dimen_area = models.DecimalField(max_digits=15,decimal_places=2)
    comments = models.TextField()
    bibliography = models.TextField()
    publications = models.TextField()
    # pictures

    def __str__(self):
        return self.title


class Tags(models.Model):
    tag = models.CharField(max_length=20)

    def __str__(self):
        return self.tag

