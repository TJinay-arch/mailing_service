from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        Group.objects.get_or_create(name="manager")

        self.stdout.write("Groups created")
