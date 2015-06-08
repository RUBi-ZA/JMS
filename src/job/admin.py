from django.contrib import admin
from job.models import *

admin.site.register(Workflow)
admin.site.register(Stage)
admin.site.register(StageType)
admin.site.register(Status)
admin.site.register(Parameter)
admin.site.register(ParameterType)
admin.site.register(ClusterJob)
