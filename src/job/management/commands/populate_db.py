from django.core.management.base import NoArgsCommand, make_option

from job.models import AccessRight, Condition, Status, ParameterType, StageType
from django.db import transaction

class Command(NoArgsCommand):

    help = "Usage: python manage.py populate_db"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
    )

    def handle_noargs(self, **options):
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
            ParameterType(ParameterTypeID=6, ParameterTypeName="Parameter value from previous stage").save()
            ParameterType(ParameterTypeID=7, ParameterTypeName="Complex object").save()
            ParameterType(ParameterTypeID=8, ParameterTypeName="Related object").save()
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
