import xml.etree.ElementTree as ET
import os, socket
from Utilities import *
from lxml import objectify

#####
# Workflow objects
#####

class Status:

    Created = 1
    Queued = 2
    Running = 3
    Completed_Successfully = 4
    Awaiting_User_Input = 5
    Stopped = 6
    Failed = 7

class ParameterType:

    Text = 1
    Number = 2
    Boolean = 3
    Options = 4
    File = 5
    Previous_Parameter = 6
    Complex_Object = 7
    Related_Object = 8


class ResultType:

    Templates = 1
    Alignment = 2
    PDB_File = 3
    Model_Validation_Scores = 4


class Editor:

    Default = 1
    Protein_Visualizer = 2
    Template_Selector = 3


class AccessRights:

    Owner = 1
    Admin = 2
    View_And_Comment = 3
    View = 4
    No_Access = 5


class DependencyCondition:

    Success = 1
    Failed = 2
    Completed = 3
    Exit_Code = 4
    
    @staticmethod
    def GetDependencyType(software, condition):
        if software == "torque":
            return {
                DependencyCondition.Success: "afterok",
                DependencyCondition.Failed: "afternotok",
                DependencyCondition.Completed: "afterany"
            }.get(condition, None)
        else:
            return None
    
    @staticmethod
    def GetArrayDependencyType(software, condition):
        if software == "torque":
            return {
                DependencyCondition.Success: "afterokarray",
                DependencyCondition.Failed: "afternotok",
                DependencyCondition.Completed: "afteranyarray"
            }.get(condition, None)
        else:
            return None
    
    
class JobStageInput:

    def __init__(self, stage_id, parameters, requires_edit):
        self.stage_id = stage_id
        self.parameters = parameters
        self.requires_edit = requires_edit


#####
# Dashboard objects
#####

class Node:
    
    def __init__(self, name, state, num_cores, busy_cores, free_cores, properties):
        self.name = name
        self.state = state
        self.num_cores = num_cores
        self.busy_cores = busy_cores
        self.free_cores = free_cores
        self.properties = properties
        self.jobs = []


class Job:
    
    def __init__(self, job_id, cores):
        self.job_id = job_id
        self.cores = cores
       

class QueueItem:
    
    def __init__(self, job_id, username, job_name, nodes, cores, state, time, queue):
        self.job_id = job_id
        self.username = username
        self.job_name = job_name
        self.nodes = nodes
        self.cores = cores
        self.state = state
        self.time = time
        self.queue = queue


class DiskUsage:

    def __init__(self, disk_size, available_space, used_space):
        self.disk_size = disk_size
        self.available_space = available_space
        self.used_space = used_space
                 

class Dashboard:

    def __init__(self, username, password):
        process = UserProcess(username, password)
        
        self.nodes = self.GetNodes(process)
        self.queue = self.GetQueue(process)        
        self.disk = self.GetDiskUsage(process, "/obiwanNFS")
        
        process.close()
                            
        
    def GetDiskUsage(self, process, path):
        out = process.run_command("df -h %s" % path)
        
        lines = out.split('\n')
        
        index = lines[0].index("Size")
        size = lines[1][index:index+5].strip()        
        used = lines[1][index+5:index+11].strip()
        available = lines[1][index+11:index+17].strip()
        
        return DiskUsage(size, available, used)
        
    
    def GetNodes(self, process):
        nodes = []
        
        out = process.run_command("qnodes -x")
        
        root = ET.fromstring(out)
        
        for node in root.iter('Node'):
            name = node.find('name').text
            state = node.find('state').text
            num_cores = int(node.find('np').text)
            properties = node.find('state').text
            busy_cores = 0;            
            
            job_dict = dict()
            
            jobs = node.find('jobs')
            if jobs is not None:            
                jobs = jobs.text
                job_cores = jobs.split(',')            
            
                for core in job_cores:
                    job_core = core.split('/')
                
                    key = job_core[1]
                    
                    core_range = job_core[0].split("-")
                    if len(core_range) > 1:
                        for i in range(int(core_range[0]), int(core_range[1])+1):                            
                            busy_cores += 1
                            if key in job_dict:
                                job_dict[key].append(i)
                            else:
                                job_dict[key] = [i]
                    else:
                        busy_cores += 1
                        if key in job_dict:
                            job_dict[key].append(job_core[0])
                        else:
                            job_dict[key] = [job_core[0]]
            
            free_cores = num_cores - busy_cores
            
            n = Node(name, state, num_cores, busy_cores, free_cores, properties)
            
            for k in job_dict:
                j = Job(k, job_dict[k])                
                n.jobs.append(j)
            
            nodes.append(n)
        
        return nodes
    
    def GetQueue(self, process):
        queue = []
        
        out = process.run_command("qstat -x")
        
        #with open("/tmp/queue.txt", "w") as f:
        #    print >> f, out
            
        try:
            data = objectify.fromstring(out)
        except:
            return queue
        
        for job in data.Job:
            job_id = str(job.Job_Id)
            username = str(job.Job_Owner).split("@")[0]
            job_name = str(job.Job_Name)
            cores = 1
            nodes = str(job.Resource_List.nodes).split(":")
            if len(nodes) > 1:
                cores = int(nodes[1].split("=")[1])
            nodes = int(nodes[0])
            state = str(job.job_state)
            time = int(job.Walltime.Remaining)
            q = str(job.queue)
            
            queue.append(QueueItem(job_id, username, job_name, nodes, cores, state, time, q))            
            
        return queue

####
# Settings objects    
####

class TorqueServer:
    
    def __init__(self, ServerName="", KeepCompleted=None, JobStatRate=None, SchedularIteration=None, NodeCheckRate=None, TCPTimeout=None, QueryOtherJobs=None, MOMJobSync=None, MoabArrayCompatible=None, Scheduling=None, ServerAdmins=[], Queues=[]):
        self.ServerName = ServerName
        self.KeepCompleted = KeepCompleted
        self.JobStatRate = JobStatRate
        self.SchedularIteration = SchedularIteration
        self.NodeCheckRate = NodeCheckRate
        self.TCPTimeout = TCPTimeout
        self.QueryOtherJobs = QueryOtherJobs
        self.MOMJobSync = MOMJobSync
        self.MoabArrayCompatible = MoabArrayCompatible
        self.Scheduling = Scheduling
        self.ServerAdministrators = ServerAdmins
        self.Queues = Queues
        
        
class ServerAdministrator:

    def __init__(self, Username=None, Host=None, Manager=None, Operator=None):
        self.Username = Username
        self.Host = Host
        self.Manager = Manager
        self.Operator = Operator
    
    
class Queue:

    def __init__(self, QueueName=None, Type=None, Enabled=None, Started=None, MaxQueable=None, MaxRun=None, MaxUserQueable=None, MaxUserRun=None, MaxNodes=None, DefaultNodes=None, MaxCPUs=None, DefaultCPUs=None, MaxMemory=None, DefaultMemory=None, MaxWalltime=None, DefaultWalltime=None, DefaultQueue=False):
        self.QueueName = QueueName
        self.Type = Type
        self.Enabled = Enabled
        self.Started = Started
        self.MaxQueable = MaxQueable
        self.MaxRun = MaxRun
        self.MaxUserQueable = MaxUserQueable
        self.MaxUserRun = MaxUserRun
        self.MaxNodes = MaxNodes
        self.DefaultNodes = DefaultNodes
        self.MaxCPUs = MaxCPUs
        self.DefaultCPUs = DefaultCPUs
        self.MaxMemory = MaxMemory
        self.DefaultMemory = DefaultMemory
        self.MaxWalltime = MaxWalltime
        self.DefaultWalltime = DefaultWalltime
        self.DefaultQueue = DefaultQueue


class Client:

    def __init__(self, NodeName=None, State=None, NumProcessors=None, Properties=None):
        self.NodeName = NodeName
        self.State = State
        self.NumProcessors = NumProcessors
        self.Properties = Properties
        
