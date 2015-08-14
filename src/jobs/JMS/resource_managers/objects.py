class ValueType:
    
    Text = 1
    Number = 2
    Checkbox = 3
    Label = 4
    Options = 5


class Status:
    
    Held = 1
    Queued = 2
    Running = 3
    Complete = 4


class ClusterJob:
    
    def __init__(self, job_id, name, user, status, output, error, working,
        exit_code=None, data_sections=[]):
            
        self.JobID = job_id
        self.JobName = name
        self.User = user
        self.Status = status
        self.ExitCode = exit_code
        self.OutputLog = output
        self.ErrorLog = error
        self.WorkingDir = working
        
        self.DataSections = data_sections


class Data:
    
    def __init__(self, DataSections, Data):
        self.DataSections = DataSections
        self.Data = Data


class DataSection:
    
    def __init__(self, SectionHeader, DataFields):
        self.SectionHeader = SectionHeader
        self.DataFields = DataFields


class DataField:
    
    def __init__(self, Key, Label, ValueType, DefaultValue, Disabled=False):
        self.Key = Key
        self.Label = Label
        self.ValueType = ValueType
        self.DefaultValue = DefaultValue
        self.Disabled = Disabled


class Dashboard:

    def __init__(self, nodes, queue, disk):
        self.nodes = nodes
        self.queue = queue        
        self.disk = disk

   
class Node:
    
    def __init__(self, name, state, num_cores, busy_cores, free_cores, other):
        self.name = name
        self.state = state
        self.num_cores = num_cores
        self.busy_cores = busy_cores
        self.free_cores = free_cores
        self.other = other
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


class SettingsSection:
    
    def __init__(self, SectionHeader, Settings):
        self.SectionHeader = SectionHeader
        self.Settings = Settings
   

class Setting:
    
    def __init__(self, Name, Value):
        self.Name = Name
        self.Value = Value


class Administrator:

    def __init__(self, AdministratorName=None, SettingsSections=[]):
        self.AdministratorName = AdministratorName
        self.SettingsSections = SettingsSections

    
class Queue:

    def __init__(self, QueueName=None, SettingsSections=[]):
        self.QueueName = QueueName
        self.SettingsSections = SettingsSections


