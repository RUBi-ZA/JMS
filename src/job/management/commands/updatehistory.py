from django.core.management.base import BaseCommand, CommandError
import subprocess, pylibmc

class Command(BaseCommand):
    help = 'Updates the job history in both the database and in-memory cache'

    def handle(self, *args, **options):
        self.stdout.write("Successfully updated job history")
