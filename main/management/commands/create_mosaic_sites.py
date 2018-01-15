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
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=True),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=True),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=True),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=True),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=True),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=False),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=False),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=False),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=False),
            Tag(tag_he=silly.title(), tag_en=silly.title(), featured=False),
        ])

        for i in range(n):
            # Create random mosaic site
            s = MosaicSite()
            s.site_id = silly.title()
            s.title_he = silly.name()
            s.title_en = silly.name()
            s.origin_he = silly.title()
            s.origin_en = silly.title()
            s.story_he = silly.thing()
            s.story_en = silly.thing()
            s.archeological_context = random.choice(['church', 'synagogue', 'public'])
            s.period = 'byzantine'
            s.video_id = silly.title()
            s.comments = silly.thing()
            s.featured = random.choice([True, False])
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
                mi.materials = [random.choice(Materials.CHOICES)[0]]
                mi.year = silly.datetime().year
                mi.displayed_at = silly.address()
                mi.description_he = silly.thing()
                mi.description_en = silly.thing()
                mi.bibliography_he = silly.thing()
                mi.bibliography_en = silly.thing()
                mi.save()
                mi.tags.add(Tag.objects.all().order_by('?')[0])
                for k in range(3):
                    mp = MosaicPicture()
                    mp.mosaic = mi
                    mp.is_cover = random.choice([True, False])
                    mp.order_priority = random.randint(1, 100)
                    filename = os.path.join(
                        settings.BASE_DIR, f'mosaic_images/{random.randint(1, 12)}.jpg'
                    )
                    mp.picture = UploadedFile(open(filename, "br"))
                    mp.negative_id = silly.number()
                    mp.photographer_name_he = silly.name()
                    mp.photographer_name_en = silly.name()
                    mp.taken_at = silly.country()
                    mp.picture_type = random.choice(PictureType.CHOICES)[0]
                    mp.taken_date = silly.datetime().date()
                    mp.comments_he = silly.thing()
                    mp.comments_en = silly.thing()
                    mp.full_clean()
                    mp.save()
                    mp.tags.add(Tag.objects.all().order_by('?')[0])
