from django.db import models
from django.contrib.auth.models import User, Group

from utilities.django.fields import CharNullField
		

class Workflow(models.Model):
	WorkflowID = models.AutoField(primary_key=True)
	WorkflowName = models.CharField(max_length=30)
	Description = models.CharField(max_length=220)
	User = models.ForeignKey(User, editable=False)
	PublicInd = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.WorkflowName
	
	class Meta:
		db_table = 'Workflows'


class StageType(models.Model):
	StageTypeID = models.IntegerField(primary_key=True)
	StageTypeName = models.CharField(max_length=30)
	
	def __unicode__(self):
		return self.StageTypeName
	
	class Meta:
		db_table = 'StageTypes'



class Stage(models.Model):
	StageID = models.AutoField(primary_key=True)
	StageName = models.CharField(max_length=100)
	StageType = models.ForeignKey(StageType, db_column='StageTypeID', related_name='Stages')	
	Workflow = models.ForeignKey(Workflow, db_column='WorkflowID', related_name='Stages')
	Command = models.CharField(max_length=100)
	StageIndex = models.IntegerField()
	
	DeletedInd = models.BooleanField(default=False)
	
	#Resources
	Queue = models.CharField(max_length=30)	
	Nodes = models.IntegerField()
	MaxCores = models.IntegerField()
	Memory = models.IntegerField()
	Walltime = models.CharField(max_length=30)	
	
	def __unicode__(self):
		return self.StageName
	
	class Meta:
		db_table = 'Stages'



class Condition(models.Model):
	ConditionID = models.IntegerField(primary_key=True)
	ConditionName = models.CharField(max_length=50)
	
	class Meta:
		db_table = "Conditions"
		
				

class StageDependency(models.Model):
	StageDependencyID = models.AutoField(primary_key=True)
	StageOI = models.ForeignKey(Stage, db_column='StageID', related_name='StageDependencies')	
	DependantOn = models.ForeignKey(Stage, db_column='DependantOnID', related_name='ReliantStages')
	Condition = models.ForeignKey(Condition, db_column='ConditionID', related_name='StageDependencies')
	ExitCodeValue = models.IntegerField(null=True, blank=True)
	
	class Meta:
		db_table = 'StageDependencies'
		
		

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
	Stage = models.ForeignKey(Stage, db_column='StageID', related_name='Parameters')	
	ParameterIndex = models.CharField(max_length=7)
	ParentParameter = models.ForeignKey('Parameter', db_column='ParentParameterID', related_name='ChildParameters', null=True, blank=True)
	Optional = models.BooleanField(default=False, db_column='OptionalInd')
	
	DeletedInd = models.BooleanField(default=False)
	
	class Meta:
		db_table = 'Parameters'



class ParameterOption(models.Model):
	ParameterOptionID = models.AutoField(primary_key=True)
	ParameterOptionText = models.CharField(max_length=30)
	ParameterOptionValue = models.CharField(max_length=30)
	Parameter = models.ForeignKey(Parameter, db_column='ParameterID', related_name='ParameterOptions')
		
	class Meta:
		db_table = 'ParameterOptions'



class InputProfile(models.Model):
    InputProfileID = models.AutoField(primary_key=True)
    InputProfileName = models.CharField(max_length=30)
    Description = models.TextField(null=True, blank=True)
    Workflow = models.ForeignKey(Workflow, db_column="WorkflowID", related_name="InputProfiles")
    
    class Meta:
        db_table = 'InputProfiles'



class InputProfileParameter(models.Model):
    InputProfileParameterID = models.AutoField(primary_key=True)
    InputProfile = models.ForeignKey(InputProfile, db_column="InputProfileID", related_name="InputProfileParameters")
    Parameter = models.ForeignKey(Parameter, db_column="ParameterID", related_name="InputProfileParameters")
    Value = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = "InputProfileParameters"



class ExpectedOutput(models.Model):
	ExpectedOutputID = models.AutoField(primary_key=True)
	ExpectedOutputFileName = models.TextField()
	Stage = models.ForeignKey(Stage, db_column="StageID", related_name="ExpectedOutputs")
	
	class Meta:
		db_table = "ExpectedOutputs"
		
		

class Status(models.Model):
	StatusID = models.IntegerField(primary_key=True)
	StatusName = models.CharField(max_length=30)
	
	def __unicode__(self):
		return self.StatusName
	
	class Meta:
		db_table = 'Status'
		
		
		
class BatchJob(models.Model):
    BatchJobID = models.AutoField(primary_key=True)
    BatchJobName = models.CharField(max_length=30)
    Description = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'BatchJobs'	
		
		

class Job(models.Model):
	JobID = models.AutoField(primary_key=True)
	JobName = models.CharField(max_length=100)
	JobDescription = models.TextField()
	Workflow = models.ForeignKey(Workflow, db_column='WorkflowID', related_name='Jobs', blank=True, null=True)
	User = models.ForeignKey(User, editable=False, related_name='Jobs')
	SubmittedAt = models.DateTimeField(null=True, blank=True)
	FinishedAt = models.DateTimeField(null=True, blank=True)
	WorkingDirectory = models.CharField(max_length=100, null=True, blank=True)
	LogsDirectory = models.CharField(max_length=100, null=True, blank=True)
	BatchJobInd = models.BooleanField(default=False)
	BatchJobID = models.ForeignKey(BatchJob, null=True, blank=True, db_column="BatchJobID", related_name="Jobs")
	
	def __unicode__(self):
		return self.JobName
	
	class Meta:
		db_table = 'Jobs'
		ordering = ['-JobID']
		
		

class JobStage(models.Model):
	JobStageID = models.AutoField(primary_key=True)
	Job = models.ForeignKey(Job, db_column='JobID', related_name='JobStages')
	Stage = models.ForeignKey(Stage, db_column='StageID', related_name='JobStages', blank=True, null=True)
	StageName = models.CharField(max_length=100, null=True, blank=True)
	ClusterJobID = models.CharField(max_length=30, null=True, blank=True, unique=True, default=None)
	State = models.ForeignKey(Status, db_column='State', related_name='JobStages', null=True, blank=True)
	RequiresEditInd = models.NullBooleanField(null=True, blank=True, default=False)
	
	#Resources
	Queue = models.CharField(max_length=30, null=True, blank=True, default=None)	
	Nodes = models.IntegerField(null=True, blank=True, default=None)
	MaxCores = models.IntegerField(null=True, blank=True, default=None)
	Memory = models.IntegerField(null=True, blank=True, default=None)
	Walltime = models.CharField(max_length=30, null=True, blank=True, default=None)
	
	class Meta:
		db_table = 'JobStages'
	
		

class ClusterJob(models.Model):
	ClusterJobID = models.CharField(max_length=30, primary_key=True)
	JobName = models.CharField(max_length=100)
	JobOwner = models.CharField(max_length=100)
	
	MemoryRequested = models.CharField(max_length=30, null=True, blank=True)
	NodesAvailable = models.CharField(max_length=30, null=True, blank=True)
	NodesRequested = models.CharField(max_length=30, null=True, blank=True)
	WalltimeRequested = models.CharField(max_length=30, null=True, blank=True)
	
	CPUTimeUsed = models.CharField(max_length=30, null=True, blank=True)
	MemoryUsed = models.CharField(max_length=30, null=True, blank=True)
	VirtualMemoryUsed = models.CharField(max_length=30, null=True, blank=True)
	WalltimeUsed = models.CharField(max_length=15, null=True, blank=True)
	
	State = models.CharField(max_length=1)
	Queue = models.CharField(max_length=30, null=True, blank=True)
	Server = models.CharField(max_length=30)
	ExecutionHost = models.CharField(max_length=100, null=True, blank=True)
	SubmitArgs = models.TextField(null=True, blank=True)
	SubmitHost = models.CharField(max_length=30, null=True, blank=True)
	OutputPath = models.CharField(max_length=200, null=True, blank=True)
	ErrorPath = models.CharField(max_length=200, null=True, blank=True)
	Priority = models.IntegerField(null=True, blank=True)
	
	CreatedTime = models.CharField(max_length=30)
	TimeEnteredQueue = models.CharField(max_length=30, null=True, blank=True)
	EligibleTime = models.CharField(max_length=30, null=True, blank=True)
	LastModified = models.CharField(max_length=30, null=True, blank=True)
	StartTime = models.CharField(max_length=30, null=True, blank=True)
	CompletionTime = models.CharField(max_length=30, null=True, blank=True)
	TotalRuntime = models.FloatField(null=True, blank=True)
	
	VariableList = models.TextField(null=True, blank=True)
	
	Comment = models.TextField(null=True, blank=True)
	ExitStatus = models.IntegerField(null=True, blank=True)	
	
	OutputStream = "Output stream not available"
	ErrorStream = "Error stream not available"
	
	class Meta:
		db_table = "ClusterJob"
		


class JobStageParameter(models.Model):
	JobStageParameterID = models.AutoField(primary_key=True)
	Parameter = models.ForeignKey(Parameter, db_column='ParameterID', related_name='JobStageParameters')
	ParameterName = models.CharField(max_length=30, null=True, blank=True, default=None)
	JobStage = models.ForeignKey(JobStage, db_column='JobStageID', related_name='JobStageParameters')
	Value = models.TextField()
	
	class Meta:
		db_table = 'JobStageParameters'	
		


class AccessRight(models.Model):
	AccessRightID = models.IntegerField(primary_key=True)
	AccessRightName = models.CharField(max_length=30)
	
	class Meta:
		db_table = 'AccessRights'
				


class UserWorkflowAccessRight(models.Model):
	UserWorkflowAccessRightID = models.AutoField(primary_key=True)
	User = models.ForeignKey(User, related_name="UserWorkflowAccessRights", db_column="UserID")
	Workflow = models.ForeignKey(Workflow, related_name="UserWorkflowAccessRights", db_column="WorkflowID")
	AccessRight = models.ForeignKey(AccessRight, related_name="UserWorkflowAccessRights", db_column="AccessRightID")
	
	class Meta:
		db_table = 'UserWorkflowAccessRights'
				


class GroupWorkflowAccessRight(models.Model):
	GroupWorkflowAccessRightID = models.AutoField(primary_key=True)
	Group = models.ForeignKey(Group, related_name="GroupWorkflowAccessRights", db_column="GroupID")
	Workflow = models.ForeignKey(Workflow, related_name="GroupWorkflowAccessRights", db_column="WorkflowID")
	AccessRight = models.ForeignKey(AccessRight, related_name="GroupWorkflowAccessRights", db_column="AccessRightID")
	
	class Meta:
		db_table = 'GroupWorkflowAccessRights'

			

class UserJobAccessRight(models.Model):
	UserJobAccessRightID = models.AutoField(primary_key=True)
	User = models.ForeignKey(User, related_name="UserJobAccessRights", db_column="UserID")
	Job = models.ForeignKey(Job, related_name="UserJobAccessRights", db_column="JobID")
	AccessRight = models.ForeignKey(AccessRight, related_name="UserJobAccessRights", db_column="AccessRightID")
	
	class Meta:
		db_table = 'UserJobAccessRights'



class GroupJobAccessRight(models.Model):
	GroupJobAccessRightID = models.AutoField(primary_key=True)
	Group = models.ForeignKey(Group, related_name="GroupJobAccessRights", db_column="GroupID")
	Job = models.ForeignKey(Job, related_name="GroupJobAccessRights", db_column="JobID")
	AccessRight = models.ForeignKey(AccessRight, related_name="GroupJobAccessRights", db_column="AccessRightID")
	
	class Meta:
		db_table = 'GroupJobAccessRights'
	
	
		
class Editor(models.Model):
	EditorID = models.AutoField(primary_key=True)
	EditorName = models.CharField(max_length=30)
	
	class Meta:
		db_table = 'Editors'
		
		
		
class ResultType(models.Model):
	ResultTypeID = models.AutoField(primary_key=True)
	ResultTypeName = models.CharField(max_length=30)
	EditableInd = models.BooleanField(default=False)
	Editor = models.ForeignKey(Editor, related_name="ResultTypes", db_column="EditorID")
	
	class Meta:
		db_table = 'ResultTypes'



class JobStageResult(models.Model):
	JobStageResultID = models.AutoField(primary_key=True)
	ResultName = models.CharField(max_length=60)
	JobStage = models.ForeignKey(JobStage, related_name="Results", db_column="JobStageID")
	ResultType = models.ForeignKey(ResultType, related_name="Results", db_column="ResultTypeID")
	ResultData = models.TextField()
	
	class Meta:
		db_table = 'JobStageResults'



class Comment(models.Model):
	CommentID = models.AutoField(primary_key=True)
	Content = models.TextField()
	User = models.ForeignKey(User, related_name="Comments", db_column="UserID")
	Job = models.ForeignKey(Job, related_name="Comments", db_column="JobID")
	
	class Meta:
		db_table = 'Comments'
