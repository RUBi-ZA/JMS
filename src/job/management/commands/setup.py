from django.core.management.base import BaseCommand, make_option
from django.conf import settings

from job.models import AccessRight, Condition, Status, ParameterType, StageType
from django.db import transaction

import os

def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
        os.chmod(path, 0775)
    print "%s created." % path

class Command(BaseCommand):
    args = '<base_url>'
    help = "Usage: python manage.py setup <base_url>"

    def handle(self, *args, **options):
        if len(args) == 1:
            print "\nSetting up shared directory:\n"
            base_path = settings.JMS_SETTINGS["JMS_shared_directory"]
            
            path = os.path.join(base_path, "users")
            create_dir(path)
            
            path = os.path.join(base_path, "workflows")
            create_dir(path)
            
            path = os.path.join(base_path, "logs/prologue")
            create_dir(path)
            
            path = os.path.join(base_path, "logs/epilogue")
            create_dir(path)
            
            path = os.path.join(base_path, "scripts")
            create_dir(path)
            
            path = os.path.join(base_path, "tmp")
            create_dir(path)
            
            with open("%s/%s" % (path, "prologue"), "w") as f:
                print >> f, "#!/bin/sh"
                print >> f, "curl <base_url>/api/jms/prologue/${2}/${1} 2> %s/logs/prologue/prologue.${1}.log" % base_path
            print "Prologue script created."
            
            with open("%s/%s" % (path, "epilogue"), "w") as f:
                print >> f, "#!/bin/sh"
                print >> f, "curl <base_url>/api/jms/epilogue/${2}/${1}/${10} 2> %s/logs/epilogue/epilogue.${1}.log" % base_path
            print "Epilogue script created."
            
            print "\nPopulating database with required data:\n"
            
            inconsistencies = 0
            with transaction.atomic():
                print "Adding access rights..."
                AccessRight(AccessRightID=1, AccessRightName="Owner").save()
                AccessRight(AccessRightID=2, AccessRightName="Admin").save()
                AccessRight(AccessRightID=3, AccessRightName="View & Use").save()
                AccessRight(AccessRightID=4, AccessRightName="View").save()
                num = len(AccessRight.objects.all())
                if num == 4:
                    print "Access rights added successfully"
                else:
                    print "There are %s access rights in the database. There should be 4. This may cause issues when running the JMS." % str(num)
                    inconsistencies += 1
                
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
                if num == 8:
                    print "Parameter types added successfully"
                else:
                    print "There are %s parameter types in the database. There should be 8. This may cause issues when running the JMS." % str(num)
                    inconsistencies += 1
                
                print "Adding stage types..."
                StageType(StageTypeID=1, StageTypeName="Command-line utility").save()
                StageType(StageTypeID=2, StageTypeName="Custom script").save()
                StageType(StageTypeID=3, StageTypeName="Workflow").save()
                num = len(StageType.objects.all())
                if num == 3:
                    print "Stage types added successfully"
                else:
                    print "There are %s stage types in the database. There should be 3. This may cause issues when running the JMS." % str(num)
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
        
        else:
            print "\nUsage: python manage.py setup <base_url>\n"
