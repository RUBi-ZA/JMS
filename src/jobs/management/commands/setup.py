from django.core.management.base import BaseCommand
from django.conf import settings

from jobs.models import Condition, Status, ParameterType
from django.db import transaction

import os

def create_dir(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, 0777)
        print "%s created." % path
    else:
        print "%s already exists." % path

class Command(BaseCommand):
    help = "Usage: python manage.py setup"
    
    def add_arguments(self, parser):
        parser.add_argument('args', nargs='*')

    def handle(self, *args, **options):
        print "\nSetting up shared directory:\n"
        base_path = settings.JMS_SETTINGS["JMS_shared_directory"]
        
        path = os.path.join(base_path, "users")
        create_dir(path)
        
        path = os.path.join(base_path, "logs/prologue")
        create_dir(path)
        
        path = os.path.join(base_path, "logs/epilogue")
        create_dir(path)
        
        path = os.path.join(base_path, "scripts")
        create_dir(path)
        
        path = os.path.join(base_path, "tmp")
        create_dir(path)
        
        print "\nPopulating database with required data:\n"
        
        inconsistencies = 0
        with transaction.atomic():
            
            print "Adding stage dependency conditions..."
            Condition(ConditionID=1, ConditionName="Stage completed successfully").save()
            Condition(ConditionID=2, ConditionName="Stage completed with errors").save()
            Condition(ConditionID=3, ConditionName="Stage completed").save()
            Condition(ConditionID=4, ConditionName="Exit code").save()
            num = len(Condition.objects.all())
            if num == 4:
                print "Conditions added successfully"
            else:
                print "There are %s conditions in the database. There should be 4. This may cause issues when running the JMS." % str(num)
                inconsistencies += 1
            
            print "Adding parameter types..."
            ParameterType(ParameterTypeID=1, ParameterTypeName="Text").save()
            ParameterType(ParameterTypeID=2, ParameterTypeName="Number").save()
            ParameterType(ParameterTypeID=3, ParameterTypeName="True/False").save()
            ParameterType(ParameterTypeID=4, ParameterTypeName="Options").save()
            ParameterType(ParameterTypeID=5, ParameterTypeName="File").save()
            ParameterType(ParameterTypeID=6, ParameterTypeName="Complex object").save()
            ParameterType(ParameterTypeID=7, ParameterTypeName="Related object").save()
            num = len(ParameterType.objects.all())
            if num == 7:
                print "Parameter types added successfully"
            else:
                print "There are %s parameter types in the database. There should be 7. This may cause issues when running the JMS." % str(num)
                inconsistencies += 1
            
            
            print "Adding possible job states..."
            Status(StatusID=1, StatusName="Created").save()
            Status(StatusID=2, StatusName="Queued").save()
            Status(StatusID=3, StatusName="Running").save()
            Status(StatusID=4, StatusName="Completed Successfully").save()
            Status(StatusID=5, StatusName="Awaiting User Input").save()
            Status(StatusID=6, StatusName="Stopped").save()
            Status(StatusID=7, StatusName="Failed").save()
            num = len(Status.objects.all())
            if num == 7:
                print "Job states added successfully"
            else:
                print "There are %s states in the database. There should be 7. This may cause issues when running the JMS." % str(num)
                inconsistencies += 1
        
        print "\nDatabase populated. %s inconsistencies were found.\n" % str(inconsistencies)
        
