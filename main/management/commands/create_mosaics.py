import random
import os

import silly
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.management.base import BaseCommand

from main.models import MosaicItem, MosaicPicture


class Command(BaseCommand):
    help = "Create new mosaics."

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, n, **options):
        for i in range(n):
            # Create random mosaic
            o = MosaicItem()
            o.title = silly.name()
            o.origin = silly.title()
            o.iaa_id = silly.title()
            o.iaa_permission_code = silly.title()
            o.period = silly.name()
            o.displayed_at = silly.adjective()
            o.dimen_length = silly.number()
            o.dimen_width = silly.number()
            o.dimen_area = silly.number()
            o.material = silly.adjective()
            o.place_name = silly.city()
            o.date = silly.datetime().date()
            o.story = silly.thing()
            o.address = silly.address()
            o.comments = silly.thing()
            o.bibliography = silly.thing()
            o.publications = silly.thing()
            o.save()

            # Add 3 random images to mosaic
            for i in range(3):
                picture = MosaicPicture()
                picture.mosaic = o
                filename = os.path.join(
                    settings.BASE_DIR, f'mosaic_images/{random.randint(1, 12)}.jpg'
                )
                picture.picture = UploadedFile(open(filename, "br"))
                picture.negative_id = silly.number()
                picture.order_priority = random.randint(1, 100)
                picture.photographer_name = silly.name()
                picture.taken_at = silly.country()
                picture.picture_type = silly.adjective()
                picture.taken_date = silly.datetime().date()
                picture.comments = silly.paragraph()
                picture.full_clean()
                picture.save()
