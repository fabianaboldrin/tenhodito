from django.contrib.staticfiles.management.commands import runserver
from django.conf import settings
from subprocess import call


class Command(runserver.Command):

    def inner_run(self, *args, **options):
        return_code = call([
            settings.WEBPACK_BIN,
            '--config',
            settings.BASE_DIR + '/webpack.config.js'
        ])
        super(Command, self).inner_run(*args, **options)
