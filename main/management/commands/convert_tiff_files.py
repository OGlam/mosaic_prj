import os

from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Convert all tiff files to jpg."

    def handle(self, **options):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT, topdown=False):
            for name in files:
                img_file = os.path.join(root, name)
                try:
                    im = Image.open(img_file)
                    if im.format == 'TIFF':
                        print("Converting {} to jpeg".format(name))
                        im.convert('RGB')
                        # Change original file to TIFF
                        new_tiff_filename = os.path.splitext(img_file)[0] + ".tiff"
                        os.rename(img_file, new_tiff_filename)
                        im.save(img_file, "JPEG", quality=100)
                except OSError as e:
                    print(e)
