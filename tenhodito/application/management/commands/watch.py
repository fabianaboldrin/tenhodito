from django.core.management.base import BaseCommand
from django.conf import settings
from subprocess import call


class Command(BaseCommand):

    def handle(self, *args, **options):
        return_code = call([
            settings.WEBPACK_BIN,
            '-w',
            '--config',
            settings.BASE_DIR + '/webpack.config.js'
        ])
