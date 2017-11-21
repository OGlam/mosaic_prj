from django.contrib import admin

# Register your models here.
from .models import Mosaic, Tags

admin.site.register(Tags)
admin.site.register(Mosaic)

