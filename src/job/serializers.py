from rest_framework import serializers
from django.contrib.auth.models import User, Group
from job.models import *

class ParameterInputProfileParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('ParameterID', 'Stage', 'ParameterType')


class InputProfileParameterSerializer(serializers.ModelSerializer):
    Parameter = ParameterInputProfileParameterSerializer()
    
    class Meta:
        model = InputProfileParameter
    
    
class InputProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InputProfile
        fields = ('InputProfileID', 'InputProfileName', 'Description')    


class InputProfileDetailSerializer(serializers.ModelSerializer):
    InputProfileParameters = InputProfileParameterSerializer(many=True)
    
    class Meta:
        model = InputProfile
        fields = ('InputProfileID', 'InputProfileName', 'Description', 'InputProfileParameters') 
        
        
class ExpectedOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpectedOutput
        
        
class WorkflowSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Workflow
        
        
class StageSerializer(serializers.ModelSerializer):
    Workflow = WorkflowSerializer()
    ExpectedOutputs = ExpectedOutputSerializer(many=True)
    
    class Meta:
        model = Stage
        fields = ('StageID', 'StageName', 'StageIndex', 'StageType', 'Workflow', 'Command', 'ExpectedOutputs')
        
        
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ('ParameterID', 'ParameterName', 'ParameterType')
        
        
class ParameterTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParameterType
        
        
class ClusterJobSerializer(serializers.ModelSerializer):
    OutputStream = serializers.Field()
    ErrorStream = serializers.Field()
        
    class Meta:
        model = ClusterJob
        
class ParameterOptionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = ParameterOption
        
        
class ParameterDetailSerializer(serializers.ModelSerializer):
    ParameterOptions = ParameterOptionSerializer(many=True)
    
    class Meta:
        model = Parameter
        
        
class StageDependencySerializer(serializers.ModelSerializer):    
    class Meta:
        model = StageDependency

        
class StageDetailSerializer(serializers.ModelSerializer):
    Parameters = ParameterDetailSerializer(many=True)
    StageDependencies = StageDependencySerializer(many=True)
    ExpectedOutputs = ExpectedOutputSerializer(many=True)
    
    class Meta:
        model = Stage
        

class WorkflowDetailSerializer(serializers.ModelSerializer):
    Stages = StageDetailSerializer(many=True)
    InputProfiles = InputProfileSerializer(many=True)
    
    class Meta:
        model = Workflow


class JobSerializer(serializers.ModelSerializer):
    Workflow = WorkflowSerializer()
    
    class Meta:
        model = Job


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class GroupSerializer(serializers.ModelSerializer):
    user_set = UserSerializer(many=True)
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'user_set')    


class AccessRightSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRight
        fields = ('AccessRightID', 'AccessRightName')


class UserJobAccessRightSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = UserJobAccessRight
        fields = ('User', 'AccessRight', 'Job')


class GroupJobAccessRightSerializer(serializers.ModelSerializer):
    Group = GroupSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = GroupJobAccessRight
        fields = ('Group', 'AccessRight', 'Job')


class JobAccessRightSerializer(serializers.ModelSerializer):
    UserJobAccessRights = UserJobAccessRightSerializer(many=True)
    GroupJobAccessRight = GroupJobAccessRightSerializer(many=True)
    
    class Meta:
        model = Workflow
        fields = ('JobID', 'JobName', 'UserJobAccessRights', 'GroupJobAccessRights')


class UserWorkflowAccessRightSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = UserWorkflowAccessRight
        fields = ('User', 'AccessRight', 'Workflow')


class GroupWorkflowAccessRightSerializer(serializers.ModelSerializer):
    Group = GroupSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = GroupWorkflowAccessRight
        fields = ('Group', 'AccessRight', 'Workflow')


class WorkflowAccessRightSerializer(serializers.ModelSerializer):
    UserWorkflowAccessRights = UserWorkflowAccessRightSerializer(many=True)
    GroupWorkflowAccessRight = GroupWorkflowAccessRightSerializer(many=True)
    
    class Meta:
        model = Workflow
        fields = ('WorkflowID', 'WorkflowName', 'UserWorkflowAccessRights', 'GroupWorkflowAccessRights')
    

#################################################################

        
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status

        
class JobStageParameterSerializer(serializers.ModelSerializer):
    Parameter = ParameterSerializer()
    
    class Meta:
        model = JobStageParameter


class ResultTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ResultType

class ResultSerializer(serializers.ModelSerializer):
    ResultType = ResultTypeSerializer()
    
    class Meta:
        model = JobStageResult
        
        
class JobStageSerializer(serializers.ModelSerializer):
    Stage = StageSerializer()
    JobStageParameters = JobStageParameterSerializer(many=True)
    
    class Meta:
        model = JobStage
        fields = ('JobStageID', 'State', 'Stage', 'JobStageParameters', 'RequiresEditInd', 'ClusterJobID')
        
        
class JobStatusSerializer(serializers.ModelSerializer):
    Workflow = WorkflowSerializer()
    Status = StatusSerializer()
    
    class Meta:
        model = Job
        fields = ('JobID', 'JobName', 'Workflow')


class GroupJobAccessRightsSerializer(serializers.ModelSerializer):
    Group = GroupSerializer()
    AccessRight = AccessRightSerializer()

    class Meta:
        model = GroupJobAccessRight
        fields = ('GroupJobAccessRightID', 'Group', 'AccessRight')


class UserJobAccessRightsSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = UserJobAccessRight
        fields = ('UserJobAccessRightID', 'User', 'AccessRight')


class CommentSerializer(serializers.ModelSerializer):
    User = UserSerializer()
    
    class Meta:
        model = Comment
        fields = ('CommentID', 'Content', 'User')


class JobDetailSerializer(serializers.ModelSerializer):
    Workflow = WorkflowSerializer()
    JobStages = JobStageSerializer(many=True)
    UserJobAccessRights = UserJobAccessRightsSerializer(many=True)
    GroupJobAccessRights = GroupJobAccessRightsSerializer(many=True)
    Comments = CommentSerializer(many=True)
    
    class Meta:
        model = Job
        fields = ('JobID', 'JobName', 'JobDescription', 'SubmittedAt', 'FinishedAt', 'Workflow', 'JobStages', 'UserJobAccessRights', 'GroupJobAccessRights', 'Comments')


class JobAccessRightSerializer(serializers.ModelSerializer):
    GroupJobAccessRights = GroupJobAccessRightsSerializer(many=True)
    UserJobAccessRights = UserJobAccessRightsSerializer(many=True)
    
    class Meta:
        model = Job
        fields = ('JobID', 'JobName', 'GroupJobAccessRights', 'UserJobAccessRights')
        

class JobGroupAccessRightsSerializer(serializers.ModelSerializer):
    Job = JobStatusSerializer()
    AccessRight = AccessRightSerializer()

    class Meta:
        model = GroupJobAccessRight
        fields = ('GroupJobAccessRightID', 'Job', 'AccessRight')
        
                
class GroupJobsSerializer(serializers.ModelSerializer):
    GroupJobAccessRights = JobGroupAccessRightsSerializer(many=True)
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'GroupJobAccessRights')


class JobUserAccessRightsSerializer(serializers.ModelSerializer):
    Job = JobStatusSerializer()
    AccessRight = AccessRightSerializer()
    
    class Meta:
        model = UserJobAccessRight
        fields = ('UserJobAccessRightID', 'Job', 'AccessRight')
        

class UserAllJobsSerializer(serializers.ModelSerializer):
    UserJobAccessRights = JobUserAccessRightsSerializer(many=True)
    groups = GroupJobsSerializer(many=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'UserJobAccessRights', 'groups')    
