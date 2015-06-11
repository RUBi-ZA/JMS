from base import *
from objects import *

from utilities import deepgetattr
from utilities.io.filesystem import Directory

from lxml import objectify

import os, subprocess, socket, xml.etree.ElementTree as ET

def GetAttr(obj, attr, default):
    try:
        return deepgetattr(obj, attr)
    except Exception, ex:
        return default

class torque(BaseResourceManager):
    
    def GetQueue(self):
        queue = []
        
        out = self.RunUserProcess("qstat -x")
            
        try:
            data = objectify.fromstring(out)
        except Exception, e:
            return queue
        
        for job in data.Job:
            job_id = str(job.Job_Id)
            username = str(job.Job_Owner).split("@")[0]
            job_name = str(job.Job_Name)
            cores = 1
            nodes = str(job.Resource_List.nodes).split(":")
            if len(nodes) > 1:
                cores = int(nodes[1].split("=")[1])
            nodes = nodes[0]
            state = str(job.job_state)
            
            try:
                time = int(job.Walltime.Remaining)
            except:
                time = "n/a"
            
            job_queue = str(job.queue)
            
            queue.append(QueueItem(job_id, username, job_name, nodes, cores, state, time, job_queue))            
            
        return queue
    
    
    def GetDetailedQueue(self):
        process = subprocess.Popen("qstat -x", shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        data = objectify.fromstring(out)
        
        f = open("/tmp/torque.log", "w")
        jobs = []
        for job in data.Job:
            #get core details to update JobStage
            exit_code = None
            state = job.job_state
            if state == 'H':
                state = Status.Held
            elif state == 'Q':
                state = Status.Queued
            elif state == 'R':
                state = Status.Running
            elif state == 'E':
                state = Status.Complete
            elif state == 'C':
                state = Status.Complete
                exit_code = job.exit_status
            
            output_path = str(GetAttr(job, 'Output_Path', 'n/a')).split(":")[1]
            error_path = str(GetAttr(job, 'Error_Path', 'n/a')).split(":")[1]
            
            env = str(GetAttr(job, 'Variable_List', 'n/a'))
            vars = env.split(',')
            
            working_dir = "~"
            for v in vars:
                kv = v.split("=")
                if kv[0] == "PBS_O_WORKDIR":
                    working_dir = kv[1]
                    flag = True
                    break
            
            c = ClusterJob(job.Job_Id, job.Job_Name, job.euser, state, 
                output_path, error_path, working_dir, exit_code, [])
            
            #get resource manager specific details
            resources_allocated = DataSection("Allocated Resources", [
                DataField(Key='mem', Label="Allocated Memory", ValueType=4, 
                    DefaultValue=str(deepgetattr(job, 'Resource_List.mem'))
                ),
                DataField(Key='nodes', Label="Allocated Nodes", ValueType=4, 
                    DefaultValue=str(deepgetattr(job, "Resource_List.nodes"))
                ),
                DataField(Key='walltime', Label="Allocated Walltime", 
                    ValueType=4, DefaultValue=str(deepgetattr(job, "Resource_List.walltime"))
                ),
                DataField(Key='queue', Label="Queue", ValueType=4, 
                    DefaultValue=str(deepgetattr(job, 'queue'))
                ),
            ])
            
            resources_used = DataSection("Resources Used", [
                DataField(Key='cput', Label="CPU Time", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'resources_used.cput', 'n/a'))
                ),
                DataField(Key='mem_used', Label="Memory Used", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'resources_used.mem', 'n/a'))
                ),
                DataField(Key='vmem', Label="Virtual Memory Used", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'resources_used.vmem', 'n/a'))
                ),
                DataField(Key='walltime_used', Label="Walltime Used", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'resources_used.walltime', 'n/a'))
                ),
                DataField(Key='exec_host', Label="Execution Node", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'exec_host', 'n/a')).split("/")[0]
                )
            ])
            
            other = DataSection("Other", [
                DataField(Key='server', Label="Server", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'server', 'n/a'))
                ),
                DataField(Key='submit_args', Label="Submit Args", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'submit_args', 'n/a'))
                ),
                DataField(Key='Output_Path', Label="Output Log", ValueType=4, 
                    DefaultValue=output_path
                ),
                DataField(Key='Error_Path', Label="Error Log", ValueType=4, 
                    DefaultValue=error_path
                ),
                DataField(Key='Priority', Label="Priority", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'Priority', 'n/a'))
                ),
                DataField(Key='Variable_List', Label="Environmental Variables", 
                    ValueType=4, DefaultValue=env
                ),
                DataField(Key='comment', Label="Comment", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'comment', 'n/a'))
                )
            ])
            
            time = DataSection("Time", [
                DataField(Key='ctime', Label="Created Time", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'ctime', 'n/a'))
                ),
                DataField(Key='qtime', Label="Time Entered Queue", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'qtime', 'n/a'))
                ),
                DataField(Key='etime', Label="Time Eligible to Run", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'etime', 'n/a'))
                ),
                DataField(Key='mtime', Label="Last Modified", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'mtime', 'n/a'))
                ),
                DataField(Key='start_time', Label="Start Time", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'start_time', 'n/a'))
                ),
                DataField(Key='comp_time', Label="Completed Time", ValueType=4, 
                    DefaultValue=str(GetAttr(job, 'comp_time', 'n/a'))
                ),
            ])
            
            c.DataSections.append(resources_allocated)
            c.DataSections.append(resources_used)
            c.DataSections.append(time)
            c.DataSections.append(other)
            
            jobs.append(c)
        
        
        f.close()
        
        return jobs
    
    
    
    
    def GetSettings(self):
        output = self.RunUserProcess('qmgr -c "print server"', expect=self.user.username + "@%s:" % socket.gethostname())
        
        data_sections = [
                DataSection(
                    SectionHeader = "Torque Settings",
                    DataFields = [
                        DataField("acl_hosts", "Server name", ValueType.Label, "", True),
                        DataField("default_queue", "Default queue", ValueType.Text, ""),
                        DataField("scheduler_iteration", "Scheduler iteration (ms)", ValueType.Number, False),
                        DataField("node_check_rate", "Node check rate (ms)", ValueType.Number, False),
                        DataField("tcp_timeout", "TCP timeout (ms)", ValueType.Number, False),
                        DataField("job_stat_rate", "Job stat rate (ms)", ValueType.Number, False),
                        DataField("keep_completed", "Keep completed time (s)", ValueType.Number, False),
                        DataField("scheduling", "Scheduling?", ValueType.Checkbox, False),
                        DataField("mom_job_sync", "Sync server with MOM jobs?", ValueType.Checkbox, False),
                        DataField("query_other_jobs", "View other users' jobs in queue?", ValueType.Checkbox, False),
                        DataField("moab_array_compatible", "Moab array compatible?", ValueType.Checkbox, False),
                    ]
                )
            ]
        
        settings_section = SettingsSection("Torque Settings", [])
        
        for line in output.split('\n'):
            
            #server details 
            if line.startswith("set server"):
                setting_line = line[11:].split("=")
                
                setting = setting_line[0].strip()
                value = setting_line[1].strip()
                
                #if the setting is a true or false value, convert the string to an actual boolean 
                if setting in ["scheduling", "query_other_jobs", "mom_job_sync", 
                    "moab_array_compatible"]:
                    value = value.lower() == "true"
                
                if setting in ["scheduling", "query_other_jobs", "mom_job_sync", 
                    "moab_array_compatible", "acl_hosts", "default_queue", 
                    "scheduler_iteration", "node_check_rate", "tcp_timeout",
                    "job_stat_rate", "keep_completed"]:
                    s = Setting(Name=setting, Value=value)
                    settings_section.Settings.append(s)
        
        settings = Data(data_sections, [settings_section])
        
        return settings
    
    
    def UpdateSettings(self, settings_sections):
        output = ""
        for section in settings_sections:
            for setting in section.Settings:
                output += self.RunUserProcess('qmgr -c "set server %s = %s"' % (setting.Name, str(setting.Value)))
        return output
    
    
    def GetQueues(self):
        output = self.RunUserProcess('qmgr -c "print server"', expect=self.user.username + "@%s:" % socket.gethostname())
        
        queue_dict = {}
        
        #set up the data structure
        data_sections = [
                DataSection(
                    SectionHeader = "General",
                    DataFields = [
                        DataField("queue_type", "Queue type", ValueType.Text, "Execution"),
                        DataField("max_queuable", "Max jobs queuable at a time", ValueType.Number, 10),
                        DataField("max_running", "Max jobs running at a time", ValueType.Number, 5),
                        DataField("enabled", "Enabled?", ValueType.Checkbox, False),
                        DataField("started", "Started?", ValueType.Checkbox, False),
                    ]
                ), DataSection(
                    SectionHeader = "User Settings",
                    DataFields = [
                        DataField("max_user_queuable", "Max jobs queuable per user", ValueType.Number, 5),
                        DataField("max_user_run", "Max jobs running per user", ValueType.Number, 1),
                    ]
                ), DataSection(
                    SectionHeader = "Resources",
                    DataFields = [
                        DataField("resources_max.mem", "Max memory", ValueType.Text, "1gb"),
                        DataField("resources_max.ncpus", "Max cores", ValueType.Number, 1),
                        DataField("resources_max.nodes", "Max nodes", ValueType.Number, 1),
                        DataField("resources_max.walltime", "Max walltime", ValueType.Text, "01:00:00"),
                        DataField("resources_default.mem", "Default memory", ValueType.Text, "1gb"),
                        DataField("resources_default.ncpus", "Default cores", ValueType.Number, 1),
                        DataField("resources_default.nodes", "Default nodes", ValueType.Number, 1),
                        DataField("resources_default.walltime", "Default walltime", ValueType.Text, "01:00:00"),
                    ]
                ), DataSection(
                    SectionHeader = "Access Control",
                    DataFields = [
                        DataField("acl_group_enable", "Enable group-based access control?", ValueType.Checkbox, False),
                        DataField("acl_user_enable", "Enable user-based access control?", ValueType.Checkbox, False),
                        DataField("acl_groups", "Groups with access", ValueType.Text, ""),
                        DataField("acl_users", "Users with access", ValueType.Text, "")
                    ]
                )
            ]
        
        acl = {}
        
        #parse the queue data
        for line in output.split('\n'):
            
            #queue details
            if line.startswith("create queue"):
                #create a queue with 3 settings sections
                queue_name = line[13:].strip()
                queue = Queue(QueueName=queue_name, SettingsSections=[
                    SettingsSection("General", []), 
                    SettingsSection("User Settings", []), 
                    SettingsSection("Resources", []), 
                    SettingsSection("Access Control", [])
                ])
                
                queue_dict[queue_name] = queue
                
            elif line.startswith("set queue"):
                setting_line = line[10:].split("=")
                
                queue_name = setting_line[0].split(" ")[0]
                queue = queue_dict[queue_name]
                
                setting = setting_line[0].split(" ")[1].strip()
                value = setting_line[1].strip()
                
                if setting in ["enabled", "started", "acl_group_enable", "acl_user_enable"]:
                    value = value.lower() == "true"
                
                #groups with access   
                if setting in ["acl_groups", "acl_groups +"]:
                    if queue_name not in acl:
                        acl[queue_name] = {
                            "groups": "",
                            "users": ""
                        }
                    
                    acl[queue_name]["groups"] += value + ","
                
                #users with access
                elif setting in ["acl_users", "acl_users +"]:
                    if queue_name not in acl:
                        acl[queue_name] = {
                            "groups": "",
                            "users": ""
                        }
                    
                    acl[queue_name]["users"] += value + ","
                
                #all other settings
                else:
                    s = Setting(Name=setting, Value=value)
                
                    if setting in ["queue_type", "max_queuable","max_running", "enabled", "started"]:
                        queue.SettingsSections[0].Settings.append(s)
                    
                    elif setting in ["max_user_queuable", "max_user_run"]:
                        queue.SettingsSections[1].Settings.append(s)
                        
                    elif setting in ["resources_max.mem", "resources_max.ncpus", "resources_max.nodes", 
                        "resources_max.walltime", "resources_default.mem", "resources_default.ncpus", 
                        "resources_default.nodes","resources_default.walltime"]:
                        queue.SettingsSections[2].Settings.append(s)
                    
                    elif setting in ["acl_group_enable", "acl_user_enable"]:
                        queue.SettingsSections[3].Settings.append(s)
        
        #add data sections and queue data to Data object
        queues = Data(data_sections, [])
        for queue_name in queue_dict:
            queue = queue_dict[queue_name]
            
            group_access = Setting(Name="acl_groups", Value=acl[queue_name]["groups"].strip(","))
            queue.SettingsSections[3].Settings.append(group_access)
            
            user_access = Setting(Name="acl_users", Value=acl[queue_name]["users"].strip(","))
            queue.SettingsSections[3].Settings.append(user_access)
            
            queues.Data.append(queue)
            
        return queues

    
    def AddQueue(self, queue_name):
        output = self.RunUserProcess('qmgr -c "create queue %s"' % queue_name)
    
    
    def UpdateQueue(self, queue):
        output = ""
        for section in queue.SettingsSections:
            for setting in section.Settings:
                #set access controls - values come as csv
                if setting.Name in ["acl_groups", "acl_users"]:
                    values = setting.Value.split(",")
                    if len(values) == 1 and values[0] == "":
                        #remove all users
                        output += self.RunUserProcess('qmgr -c "set queue %s %s = temp"' % (queue.QueueName, setting.Name))
                        output += self.RunUserProcess('qmgr -c "set queue %s %s -= temp"' % (queue.QueueName, setting.Name))
                    else:
                        for index, value in enumerate():
                            value = value.strip()
                            if index == 0:
                                output += self.RunUserProcess('qmgr -c "set queue %s %s = %s"' % (queue.QueueName, setting.Name, value))
                            else:
                                output += self.RunUserProcess('qmgr -c "set queue %s %s += %s"' % (queue.QueueName, setting.Name, value))
                    
                output += self.RunUserProcess('qmgr -c "set queue %s %s = %s"' % (queue.QueueName, setting.Name, str(setting.Value)))
        return output
    
    
    def DeleteQueue(self, queue_name):       
        output = self.RunUserProcess('qmgr -c "delete queue %s"' % queue_name)
    
    
    def GetAdministrators(self):
        output = self.RunUserProcess('qmgr -c "print server"', expect=self.user.username + "@%s:" % socket.gethostname())
        
        data_sections = [
                DataSection(
                    SectionHeader = "Privileges",
                    DataFields = [
                        DataField("managers", "Manager?", ValueType.Checkbox, False),
                        DataField("operators", "Operator?", ValueType.Checkbox, False)
                    ]
                )
            ]
        
        admins = {}
        
        for line in output.split('\n'):
            
            #server details 
            if line.startswith("set server"):
                setting_line = line[11:].split("=")
                
                setting = setting_line[0].strip().strip(" +")
                value = setting_line[1].strip()
                
                
                #the managers setting forms part of the admin object
                if setting == "managers" or setting == "managers +":
                    setting = Setting(Name=setting, Value=True)
                    if value in admins:
                        admins[value].SettingsSections[0].Settings.append(setting)
                    else:
                        Section = SettingsSection(SectionHeader="Privileges", Settings=[setting])
                        admins[value] = Administrator(AdministratorName=value, SettingsSections=[Section]) 
                #the operators setting also forms part of the admin object
                elif setting == "operators" or setting == "operators +":
                    setting = Setting(Name=setting, Value=True)
                    if value in admins:
                        admins[value].SettingsSections[0].Settings.append(setting)
                    else:
                        Section = SettingsSection(SectionHeader="Privileges", Settings=[setting])
                        admins[value] = Administrator(AdministratorName=value, SettingsSections=[Section])
        
        administrators = Data(data_sections, [])
        for k in admins:
            administrators.Data.append(admins[k])
        
        return administrators
    
    
    def AddAdministrator(self, administrator_name):
        output = self.RunUserProcess('qmgr -c "set server managers += %s"' % (administrator_name))
        output += self.RunUserProcess('qmgr -c "set server operators += %s"' % (administrator_name))
        return output
    
    
    def UpdateAdministrator(self, administrator):
        output = ""
        for section in administrator.SettingsSections:
            for setting in section.Settings:
                if setting.Value:
                    output += "\n" + self.RunUserProcess('qmgr -c "set server %s += %s"' % (setting.Name, administrator.AdministratorName))
                else:
                    output += "\n" + self.RunUserProcess('qmgr -c "set server %s -= %s"' % (setting.Name, administrator.AdministratorName))
        return output
    
    
    def DeleteAdministrator(self, administrator_name):
        output = "\n" + self.RunUserProcess('qmgr -c "set server managers -= %s"' % administrator_name)
        output += "\n" + self.RunUserProcess('qmgr -c "set server operators -= %s"' % administrator_name)
        return output
    
    
    def GetNodes(self):
        nodes = []
        
        out = self.RunUserProcess("qnodes -x")
        
        root = ET.fromstring(out)
        
        for node in root.iter('Node'):
            name = node.find('name').text
            state = node.find('state').text
            num_cores = int(node.find('np').text)
            properties = node.find('properties').text
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
    
    
    def AddNode(self, node):
        output = self.RunUserProcess('qmgr -c "create node %s"' % node.name)   
        self.UpdateNode(node)
    
    
    def UpdateNode(self, node):    
        output = self.RunUserProcess('qmgr -c "set node %s np = %s"' % (node.name, str(node.num_cores)))
        output += self.RunUserProcess('qmgr -c "set node %s properties = %s"' % (node.name, node.other))
    
    
    def DeleteNode(self, id):
        output = self.RunUserProcess('qmgr -c "delete node %s"' % id) 
    
    
    def Stop(self):
        return self.RunUserProcess("qterm -t quick")
    
    
    def Start(self):
        return self.RunUserProcess("qserverd", sudo=True)
    
    
    def Restart(self):
        output = self.Stop()
        output += self.Start()
        return output
    
    
    def GetDefaultResources(self):
        return DataSection("torque", [
            DataField(
                Key = "nodes",
                Label = "Nodes",
                ValueType = ValueType.Number,
                DefaultValue = 1,
                Disabled = False
            ), DataField(
                Key = "ppn",
                Label = "Cores",
                ValueType = ValueType.Number,
                DefaultValue = 1,
                Disabled = False
            ), DataField(
                Key = "mem",
                Label = "Memory (GB)",
                ValueType = ValueType.Number,
                DefaultValue = 1,
                Disabled = False
            ), DataField(
                Key = "walltime",
                Label = "Walltime (h:m:s)",
                ValueType = ValueType.Text,
                DefaultValue = "01:00:00",
                Disabled = False
            ), DataField(
                Key = "queue",
                Label = "Queue",
                ValueType = ValueType.Text,
                DefaultValue = "batch",
                Disabled = False
            ), DataField(
                Key = "variables",
                Label = "Environmental Variables",
                ValueType = ValueType.Text,
                DefaultValue = "",
                Disabled = False
            )
        ])

    
    def CreateJobScript(self, job_name, job_dir, script_name, settings, 
        dependencies, commands):
        #assert len(section.DataFields) == 6, "Not enough data fields"
        
        log_dir = os.path.join(job_dir, "logs")
        Directory.create_directory(log_dir)
        
        script = os.path.join(job_dir, script_name)
        
        with open(script, 'w') as job_script:
            print >> job_script, "#!/bin/sh"
            print >> job_script, "#PBS -o localhost:%s" % os.path.join(log_dir, "output.log")
            print >> job_script, "#PBS -e localhost:%s" % os.path.join(log_dir, "error.log")
            print >> job_script, "#PBS -d %s" % job_dir
            print >> job_script, "#PBS -N %s" % job_name
            
            nodes = ""
            for setting in settings:
                if setting.Name == "nodes":
                    nodes += "#PBS -l nodes=%s" % setting.Value
                elif setting.Name == "ppn":
                    nodes += ":ppn=%s" % setting.Value
                elif setting.Name == "mem":
                    print >> job_script, "#PBS -l mem=%sgb" % setting.Value
                elif setting.Name == "walltime":
                    print >> job_script, "#PBS -l walltime=%s" % setting.Value
                elif setting.Name == "queue":
                    print >> job_script, "#PBS -q %s" % setting.Value
                elif setting.Name == "variables":
                    if setting.Value.strip() != "":
                        print >> job_script, "#PBS -v %s" % setting.Value
                    else:
                        print >> job_script, "#PBS -V"
            print >> job_script, nodes 
            
            #TODO: set dependencies
            
            print >> job_script, ""
            print >> job_script, commands   
        
        return script
    
    
    def ExecuteJobScript(self, script):
        return self.RunUserProcess("qsub %s" % script)
    
    
    def KillJob(self, id):
        return self.RunUserProcess("qdel %s" % id)
    
    
    def AlterJob(self, Key, Value):
        raise NotImplementedError
    
    
    
    
    