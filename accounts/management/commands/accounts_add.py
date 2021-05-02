import json

from django.core.management.base import BaseCommand, CommandError

from common.utils import ModelManager


class Command(BaseCommand):
    help = 'Creates a new Accounts object Model'

    def add_arguments(self, parser):
        parser.add_argument('model_name', type=str)
        parser.add_argument('json_data', type=str)

    def handle(self, *args, **options):
        model_name = '{0}{1}'.format(
            options['model_name'].lower(),
            'model' if 'model' not in options['model_name'].lower() else '')
        json_data = options['json_data']
        try:
            object_data = json.loads(json_data)
        except json.JSONDecodeError:
            raise CommandError('%s json_data cannot be correctly deserialized' % json_data)

        try:
            item = ModelManager.handle(
                f'accounts.{model_name}', 'create', **object_data)
        except Exception as err:
            raise CommandError('An error occurred while creating the Workspace: %s' % err)

        self.stdout.write(self.style.SUCCESS(
            'Successfully created "%s" uuid="%s"' % (model_name, item.uuid)))
