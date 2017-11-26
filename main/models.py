from django.db import models

# Create your models here.




class Tags(models.Model):
    tags = models.CharField(max_length=20)

    def __str__(self):
        return self.tags


class Mosaic(models.Model):
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
    matriel = models.CharField(max_length=50)
    dimen_length = models.DecimalField(max_digits=10, decimal_places=2)
    dimen_width = models.DecimalField(max_digits=10, decimal_places=2)
    dimen_area = models.DecimalField(max_digits=15, decimal_places=2)
    comments = models.TextField(blank = True)
    bibliography = models.TextField(blank = True)
    publications = models.TextField(blank = True)

    # pictures

    def __str__(self):
        return self.title


class MosaicPicture(models.Model):
    mosaic = models.ForeignKey (Mosaic, on_delete=models.CASCADE)
    order_priorety = models.IntegerField (default=100)
    picture = models.ImageField(upload_to='mosaic_pictures')
    negative_id = models.CharField(max_length=50)
    photographer_name = models.CharField(max_length=100)
    taken_at = models.CharField(blank = True, max_length=100)
    picture_type = models.CharField(max_length=50)
    taken_date = models.DateField()
    comments = models.TextField(blank = True)

    def __str__(self):
        return self.negative_id
