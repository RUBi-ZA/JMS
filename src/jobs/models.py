from django.db import models
from django.contrib.auth.models import User, Group

class Reference(models.Model):
    ReferenceID = models.AutoField(primary_key=True)
    FirstNames = models.CharField(max_length=100)
    Surname = models.CharField(max_length=45)
    Title = models.CharField(max_length=10)
    Affiliation = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return "%s, %s" % (self.Surname, self.FirstNames)
    
    class Meta:
        db_table = 'References'
        

class Status(models.Model):
    StatusID = models.IntegerField(primary_key=True)
    StatusName = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.StatusName
    
    class Meta:
        db_table = 'Status'


class Category(models.Model):
    CategoryID = models.AutoField(primary_key=True)
    CategoryName = models.CharField(max_length=30)
    
    def __unicode__(self):
        return self.CategoryName
    
    class Meta:
        db_table = 'Categories'


class Tool(models.Model):
    ToolID = models.AutoField(primary_key=True)
    ToolName = models.CharField(max_length=30)
    Category = models.ForeignKey(Category, db_column="CategoryID", related_name="Tools")
    ToolDescription = models.CharField(max_length=100, null=True, blank=True)
    User = models.ForeignKey(User, editable=False)
    PublicInd = models.BooleanField(default=False)
    
    DeletedInd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.ToolName
    
    class Meta:
        db_table = 'Tools'


class ToolReference(models.Model):
    ToolReferenceID = models.AutoField(primary_key=True)
    Tool = models.ForeignKey(Tool, db_column="ToolID", related_name="ToolReferences")
    Reference = models.ForeignKey(Reference, db_column="ReferenceID", related_name="ReferenceTools")
    
    class Meta:
        unique_together = ('Tool', 'Reference',)
        db_table = 'ToolReferences'


class ToolVersion(models.Model):
    ToolVersionID = models.AutoField(primary_key=True)
    Tool = models.ForeignKey(Tool, db_column="ToolID", related_name="ToolVersions")
    ToolVersionNum = models.CharField(max_length=30)
    ShortDescription = models.CharField(max_length=100, null=True, blank=True)
    LongDescription = models.TextField(null=True, blank=True)
    Command = models.TextField()
    DatePublished = models.DateField(auto_now=True)
    
    DeletedInd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.ToolVersionID
    
    class Meta:
        ordering = ['-ToolVersionID']
        unique_together = ('Tool', 'ToolVersionNum',)
        db_table = 'ToolVersions'


class ToolVersionResource(models.Model):
    ToolVersionResourceID = models.AutoField(primary_key=True)
    ResourceManager = models.CharField(max_length=30)
    ToolVersion = models.ForeignKey(ToolVersion, db_column='ToolVersionID', related_name='Resources')  
    Key = models.CharField(max_length=15)
    Value = models.CharField(max_length=255)
    Label = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('ResourceManager', 'ToolVersion', 'Key')
        db_table = 'ToolVersionResources'


class ParameterType(models.Model):
    ParameterTypeID = models.IntegerField(primary_key=True)
    ParameterTypeName = models.CharField(max_length=40, db_column='ParameterName')
    
    class Meta:
        db_table = 'ParameterTypes'

    
class Parameter(models.Model):
    ParameterID = models.AutoField(primary_key=True)
    ParameterName = models.CharField(max_length=30)
    Context = models.CharField(max_length=100)
    InputBy = models.CharField(max_length=20)
    Value = models.TextField()
    Multiple = models.BooleanField(default=False)    
    ParameterType = models.ForeignKey(ParameterType, db_column='ParameterTypeID', related_name='Parameters')
    Delimiter = models.CharField(max_length=10, null=True, blank=True)
    ToolVersion = models.ForeignKey(ToolVersion, db_column='ToolVersionID', related_name='ToolParameters')    
    ParameterIndex = models.CharField(max_length=7)
    ParentParameter = models.ForeignKey('Parameter', db_column='ParentParameterID', related_name='ChildParameters', null=True, blank=True)
    Optional = models.BooleanField(default=False, db_column='OptionalInd')
    
    DeletedInd = models.BooleanField(default=False)
    
    class Meta:
        #unique_together = (('ToolVersion', 'ParameterIndex', 'ParentParameter',),)
        db_table = 'Parameters'



class ParameterOption(models.Model):
    ParameterOptionID = models.AutoField(primary_key=True)
    ParameterOptionText = models.CharField(max_length=30)
    ParameterOptionValue = models.CharField(max_length=30)
    Parameter = models.ForeignKey(Parameter, db_column='ParameterID', related_name='ParameterOptions')
    
    DeletedInd = models.BooleanField(default=False)
        
    class Meta:
        db_table = 'ParameterOptions'


class Workflow(models.Model):
    WorkflowID = models.AutoField(primary_key=True)
    WorkflowName = models.CharField(max_length=30)
    Category = models.ForeignKey(Category, db_column="CategoryID", related_name="Workflows")
    Description = models.CharField(max_length=100)
    User = models.ForeignKey(User, editable=False)
    PublicInd = models.BooleanField(default=False)
    
    DeletedInd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.WorkflowName
    
    class Meta:
        db_table = 'Workflows'


class WorkflowReference(models.Model):
    WorkflowReferenceID = models.AutoField(primary_key=True)
    Workflow = models.ForeignKey(Workflow, db_column="ToolID", related_name="WorkflowReferences")
    Reference = models.ForeignKey(Reference, db_column="ReferenceID", related_name="ReferenceWorkflows")
    
    class Meta:
        unique_together = ('Workflow', 'Reference',)
        db_table = 'WorkflowReferences'


class WorkflowVersion(models.Model):
    WorkflowVersionID = models.AutoField(primary_key=True)
    Workflow = models.ForeignKey(Workflow, db_column="WorkflowID", related_name="WorkflowVersions")
    WorkflowVersionNum = models.CharField(max_length=30)
    ShortDescription = models.CharField(max_length=100, null=True, blank=True)
    LongDescription = models.TextField(null=True, blank=True)
    DatePublished = models.DateField(auto_now=True)
    
    DeletedInd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.WorkflowVersionNum
    
    class Meta:
        unique_together = ('Workflow', 'WorkflowVersionNum',)
        db_table = 'WorkflowVersions'


class UserToolPermission(models.Model):
    UserToolPermissionID = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, editable=False)
    Tool = models.ForeignKey(Tool, db_column="ToolID", related_name="UserToolPermissions")
    Run = models.BooleanField(default=True)
    Export = models.BooleanField(default=False)
    Edit = models.BooleanField(default=False)
    Publish = models.BooleanField(default=False)
    Admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('User', 'Tool',)
        db_table = 'UserToolPermissions'


class UserWorkflowPermission(models.Model):
    UserWorkflowPermissionID = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, editable=False)
    Workflow = models.ForeignKey(Workflow, db_column="WorkflowID", related_name="UserWorkflowPermissions")
    Run = models.BooleanField(default=True)
    Export = models.BooleanField(default=False)
    Edit = models.BooleanField(default=False)
    Publish = models.BooleanField(default=False)
    Admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('User', 'Workflow',)
        db_table = 'UserWorkflowPermissions'
    

class Stage(models.Model):
    StageID = models.AutoField(primary_key=True, db_column="WorkflowToolID")
    WorkflowVersion = models.ForeignKey(WorkflowVersion, db_column="WorkflowVersionID", related_name="WorkflowVersionStages")
    ToolVersion = models.ForeignKey(ToolVersion, db_column="ToolVersionID", related_name="ToolVersionStages", null=True, blank=True)
    SubWorkflowVersion = models.ForeignKey('WorkflowVersion', db_column="SubWorkflowVersionID", related_name="WorkflowVersionWorkflows", null=True, blank=True)
    Checkpoint = models.BooleanField(default=False)
    StageLevel = models.IntegerField(default=0)

    left_co_ord = models.IntegerField()
    top_co_ord = models.IntegerField()
    
    class Meta:
        db_table = 'Stages'


class Condition(models.Model):
    ConditionID = models.IntegerField(primary_key=True)
    ConditionName = models.CharField(max_length=50)
    
    class Meta:
        db_table = "Conditions"


class StageDependency(models.Model):
    StageDependencyID = models.AutoField(primary_key=True)
    StageOI = models.ForeignKey(Stage, db_column="StageID", related_name="StageDependencies")
    DependantOn = models.ForeignKey(Stage, db_column="DependantOnID", related_name="ReliantStages")
    Condition = models.ForeignKey(Condition, db_column='ConditionID', related_name='ConditionsStageDependencies')
    ExitCodeValue = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'StageDependencies'


class StageParameter(models.Model):
    StageParameterID = models.AutoField(primary_key=True)
    Stage = models.ForeignKey(Stage, db_column="StageID", related_name="StageParameters")
    Parameter = models.ForeignKey(Parameter, db_column="ParameterID", related_name="ParameterStages")
    StageParameterType = models.IntegerField(db_column="StageParameterTypeID") # 1 = Value, 2 = Previous Parameter, 3 = Expected output
    Value = models.TextField()
    
    class Meta:
        unique_together = ('Stage', 'Parameter')
        db_table = 'StageParameters'


class InputProfile(models.Model):
    InputProfileID = models.AutoField(primary_key=True)
    InputProfileName = models.CharField(max_length=30)
    Description = models.TextField(null=True, blank=True)
    WorkflowVersion = models.ForeignKey(WorkflowVersion, db_column="WorkflowVersionID", related_name="InputProfiles")
    
    DeletedInd = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'InputProfiles'


class InputProfileParameter(models.Model):
    InputProfileParameterID = models.AutoField(primary_key=True)
    InputProfile = models.ForeignKey(InputProfile, db_column="InputProfileID", related_name="InputProfileParameters")
    Parameter = models.ForeignKey(Parameter, db_column="ParameterID", related_name="InputProfileParameters")
    Value = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "InputProfileParameters"

    
class BatchJob(models.Model):
    BatchJobID = models.AutoField(primary_key=True)
    BatchJobName = models.CharField(max_length=30)
    Description = models.TextField(null=True, blank=True)
    
    DeletedInd = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'BatchJobs'


class Job(models.Model):
    JobID = models.AutoField(primary_key=True)
    JobName = models.CharField(max_length=100)
    JobDescription = models.TextField()
    WorkflowVersion = models.ForeignKey(WorkflowVersion, db_column='WorkflowVersionID', related_name='WorkflowVersionJobs', blank=True, null=True)
    ToolVersion = models.ForeignKey(ToolVersion, db_column='ToolVersionID', related_name='ToolVersionJobs', blank=True, null=True)
    User = models.ForeignKey(User, editable=False, related_name='Jobs')
    SubmittedAt = models.DateTimeField(auto_now=True)
    FinishedAt = models.DateTimeField(null=True, blank=True)
    BatchJobInd = models.BooleanField(default=False)
    BatchJobID = models.ForeignKey(BatchJob, null=True, blank=True, db_column="BatchJobID", related_name="Jobs")
    
    JobTypeID = models.IntegerField() #1-Custom, 2-Tool, 3-Workflow, 4-External
    
    DeletedInd = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.JobName
    
    class Meta:
        db_table = 'Jobs'
        ordering = ['-JobID']


class UserJobPermission(models.Model):
    UserJobPermissionID = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, editable=False)
    Job = models.ForeignKey(Job, db_column="JobID", related_name="UserJobPermissions")
    View = models.BooleanField(default=True)
    Repeat = models.BooleanField(default=False)
    Share = models.BooleanField(default=False)
    Admin = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('User', 'Job',)
        db_table = 'UserJobPermissions'
    

class JobStage(models.Model):
    JobStageID = models.AutoField(primary_key=True)
    Job = models.ForeignKey(Job, db_column="JobID", related_name="JobStages")
    Stage = models.ForeignKey(Stage, db_column="StageID", related_name="StageJobs", null=True, blank=True)
    ToolName = models.CharField(max_length=100, null=True, blank=True)
    Commands = models.TextField(null=True, blank=True)
    Status = models.ForeignKey(Status, db_column='StatusID', related_name='StatusJobStages', null=True, blank=True)
    RequiresEditInd = models.NullBooleanField(null=True, blank=True, default=False)
    ExitCode = models.IntegerField(null=True, blank=True)
    ClusterJobID = models.CharField(max_length=30, unique=True, null=True, blank=True)
    JobData = models.TextField()
    
    ErrorLog = models.CharField(max_length=255, null=True, blank=True)
    OutputLog = models.CharField(max_length=255, null=True, blank=True)
    WorkingDirectory = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'JobStages'


class JobStageResource(models.Model):
    JobStageResourceID = models.AutoField(primary_key=True)
    ResourceManager = models.CharField(max_length=30)
    JobStage = models.ForeignKey(JobStage, db_column='JobStageID', related_name='JobStageResources')  
    Key = models.CharField(max_length=15)
    Value = models.CharField(max_length=255)
    Label = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('ResourceManager', 'JobStage', 'Key')
        db_table = 'JobStageResources'


class JobStageDependency(models.Model):
    JobStageDependencyID = models.AutoField(primary_key=True)
    JobStageOI = models.ForeignKey(JobStage, db_column="JobStageID", related_name="JobStageDependencies")
    DependantOn = models.ForeignKey(JobStage, db_column="DependantOnID", related_name="ReliantJobStages")
    Condition = models.ForeignKey(Condition, db_column='ConditionID', related_name='ConditionsJobStageDependencies')
    ExitCodeValue = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'JobStageDependencies'


class JobStageDataSection(models.Model):
    DataSectionID = models.AutoField(primary_key=True)
    DataSectionName = models.CharField(max_length=30)
    JobStage = models.ForeignKey(JobStage, db_column="JobStageID", related_name="DataSections")
    
    class Meta:
        db_table = "JobStageDataSections"
    

class JobStageDataField(models.Model):  
    DataFieldID = models.AutoField(primary_key=True)
    JobStageDataSection = models.ForeignKey(JobStageDataSection, db_column="DataSectionID", related_name="DataFields")
    Key = models.CharField(max_length=45)
    Value = models.TextField()
    Label = models.CharField(max_length=100)
    ValueType = models.IntegerField()
    
    class Meta:
        unique_together = ('JobStageDataSection', 'Key',)
        db_table = 'JobStageDataFields'


class JobStageParameter(models.Model):
    JobStageParameterID = models.AutoField(primary_key=True)
    Parameter = models.ForeignKey(Parameter, db_column='ParameterID', related_name='ParameterJobTools')
    ParameterName = models.CharField(max_length=30, null=True, blank=True, default=None)
    JobStage = models.ForeignKey(JobStage, db_column='JobStageID', related_name='JobStageParameters')
    Value = models.TextField()
    
    class Meta:
        db_table = 'JobStageParameters'    



class FileType(models.Model):
    FileTypeID = models.AutoField(primary_key=True)
    FileTypeName = models.CharField(max_length=30)
    
    class Meta:
        db_table = 'FileTypes'



class ExpectedOutput(models.Model):
    ExpectedOutputID = models.AutoField(primary_key=True)
    OutputName = models.CharField(max_length=30)
    FileName = models.CharField(max_length=256)
    FileType = models.ForeignKey(FileType, db_column='FileTypeID', related_name='FileOutputs')
    ToolVersion = models.ForeignKey(ToolVersion, db_column='ToolVersionID', related_name='ExpectedOutputs')
    
    class Meta:
        db_table = 'ExpectedOutputs'
    