from django.core.management.base import BaseCommand
from core.models import GroupCategory


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_tags(self):
        d = GroupCategory()
        d.name = '에이대학교'
        d.domain = 'auniv.ac.kr'
        d.group_code = 1
        d.save()

    def handle(self, *args, **options):
        self._create_tags()
