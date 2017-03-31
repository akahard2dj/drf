from django.core.management.base import BaseCommand
from core.models.category import (University, Department)
from core.models.name_tag import NameTag


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_univ(self):
        a = University()
        a.name = '에이대학교'
        a.domain = 'auniv.ac.kr'
        a.save()

        b = University()
        b.name = '비이대학교'
        b.domain = 'buniv.ac.kr'
        b.save()

        c = University()
        c.name = '씨이대학교'
        c.domain = 'cuniv.ac.kr'
        c.save()

        d = University()
        d.name = '디이대학교'
        d.domain = 'duniv.ac.kr'
        d.save()

    def _create_dept(self):
        a = Department()
        a.name = '인문학'
        a.save()

        b = Department()
        b.name = '자연/공학'
        b.save()

        c = Department()
        c.name = '의치학과'
        c.save()

        d = Department()
        d.name = '예체능'
        d.save()

    def _create_name_tag(self):
        a = NameTag()
        a.group_title = 'auniv'
        a.save()
        a.university.add(University.objects.get(domain='auniv.ac.kr'))


        b = NameTag()
        b.group_title = 'buniv'
        b.save()
        b.university.add(University.objects.get(domain='buniv.ac.kr'))


        c = NameTag()
        c.group_title = 'cuniv'
        c.save()
        c.university.add(University.objects.get(domain='cuniv.ac.kr'))


        d = NameTag()
        d.group_title = 'duniv'
        d.save()
        d.university.add(University.objects.get(domain='duniv.ac.kr'))

        e = NameTag()
        e.group_title = 'auniv/buniv'
        e.save()
        e.university.add(University.objects.get(domain='auniv.ac.kr'))
        e.university.add(University.objects.get(domain='buniv.ac.kr'))

    def handle(self, *args, **options):
        self._create_univ()
        self._create_dept()
        self._create_name_tag()