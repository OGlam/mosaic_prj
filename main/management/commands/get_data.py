from django.core.management.base import BaseCommand

from main.get_data import get_data


class Command(BaseCommand):
    help = "Get data from excel."

    def handle(self, **options):
        get_data()
