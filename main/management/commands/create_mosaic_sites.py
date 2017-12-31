import random
import os

import silly
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.management.base import BaseCommand

from main.models import MosaicItem, MosaicPicture, MosaicSite, Tag, Materials, PictureType


class Command(BaseCommand):
    help = "Create new mosaic sites."

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, n, **options):
        # Create 5 tags
        Tag.objects.bulk_create([
            Tag(tag_he=silly.title(), tag_en=silly.title()),
            Tag(tag_he=silly.title(), tag_en=silly.title()),
            Tag(tag_he=silly.title(), tag_en=silly.title()),
            Tag(tag_he=silly.title(), tag_en=silly.title()),
            Tag(tag_he=silly.title(), tag_en=silly.title()),
        ])

        for i in range(n):
            # Create random mosaic site
            s = MosaicSite()
            s.site_id = silly.title()
            s.title = silly.name()
            s.origin = silly.title()
            s.story = silly.thing()
            s.archeological_context = ['church', 'synagogue', 'public'][random.randint(0, 2)]
            s.period = 'byzantine'
            s.video_id = silly.title()
            s.comments = silly.thing()
            s.featured = [True, False][random.randint(0, 1)]
            s.latitude = silly.number()
            s.longitude = silly.number()
            s.save()
            for j in range(3):
                mi = MosaicItem()
                mi.mosaic_site = s
                mi.misp_rashut = silly.title()
                mi.length = silly.number()
                mi.width = silly.number()
                mi.area = silly.number()
                mi.rishayon = silly.title()
                mi.materials = [Materials.CHOICES[random.randint(0, len(Materials.CHOICES) - 1)][0]]
                mi.year = silly.datetime().year
                mi.displayed_at = silly.address()
                mi.bibliography = silly.thing()
                mi.save()
                mi.tags.add(Tag.objects.all().order_by('?')[0])
                for k in range(3):
                    mp = MosaicPicture()
                    mp.mosaic = mi
                    mp.is_cover = [True, False][random.randint(0, 1)]
                    mp.order_priority = random.randint(1, 100)
                    filename = os.path.join(
                        settings.BASE_DIR, f'mosaic_images/{random.randint(1, 12)}.jpg'
                    )
                    mp.picture = UploadedFile(open(filename, "br"))
                    mp.negative_id = silly.number()
                    mp.photographer_name = silly.name()
                    mp.taken_at = silly.country()
                    mp.picture_type = PictureType.CHOICES[random.randint(0, len(PictureType.CHOICES) - 1)][0]
                    mp.taken_date = silly.datetime().date()
                    mp.comments = silly.thing()
                    mp.full_clean()
                    mp.save()
                    mp.tags.add(Tag.objects.all().order_by('?')[0])
