from django.core.management.base import BaseCommand, CommandError
from job.models import JMS

class Command(BaseCommand):
    help = 'Updates the job history in both the database and in-memory cache'

    def handle(self, *args, **options):
        jms = JMS()
        jms.UpdateJobHistory()
        self.stdout.write("Successfully updated job history")
