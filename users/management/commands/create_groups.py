from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        Group.objects.get_or_create(name="manager")

        self.stdout.write("Groups created")