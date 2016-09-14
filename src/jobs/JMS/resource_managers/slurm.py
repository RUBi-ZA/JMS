from base import *
from objects import *

import os, sys, time, datetime, socket, re

class slurm(BaseResourceManager):

    def GetQueue(self):
        column_names = ["Job ID", "Username", "Queue", "Job Name", "State", "Nodes", "Cores", "Time Requested", "Time Used"]
        rows = []
        
        queue = JobQueue(column_names, rows)
        
        try:
            out = self.RunUserProcess('/mounts/rey/software/slurm/bin/squeue -o "%F %u %P %j %T %R %C %l %M"')
            data = out.splitlines()

        except Exception, e:
            return queue
            
        for job in data:
            line = job.split()
            if "JOB_ID" not in line[0]:
                job_id = line[0]
                user = line[1]
                partition = line[2] # Queue
                job_name = line[3]
                state = line[4]
                
                if state == "SUSPENDED" or state == "BOOT_FAIL" or state == "CANCELLED" or state == "CONFIGURING":
                    state = Status.Held
                elif state == "PENDING":
                    state = Status.Queued
                elif state == "RUNNING" or state == "COMPLETING":
                    state = Status.Running
                elif state == "COMPLETED" or state == "FAILED" or state == "NODE_FAIL" or state == "PREEMPTED" or state == "SPECIAL_EXIT" or state == "STOPPED" or state == "TIMEOUT":
                    state = Status.Complete
                
                nodes = line[5]
                cores = line[6]
                time_requested = line[7]
                time_used = line[8]
                
                row = [
                    str(user),
                    str(partition),
                    str(job_name),
                    str(line[4].lower()),
                    nodes,
                    cores,
                    str(time_requested),
                    time_used
                ]
        
                queue.rows.append(QueueRow(str(job_id), state, row))
            
        return queue
    
    def GetJob(self, id):
        out = self.RunUserProcess('/mounts/rey/software/slurm/bin/squeue -j {0} -o "%r %t %Z %r %F %j %u %m %D %l %P %C N/A %d %M %B %V %S %e %o %p %k"'.format(id) )

        data = out.splitlines()
        return self._ParseJob(data[1])


    def _ParseJob(self, data):
        job = data.strip().split()

        #get core details to update JobStage
        exit_code = job[0]
        state = job[1]
        '''
        if state == 'H':
            state = Status.Held
        elif state == 'Q':
            state = Status.Queued
        elif state == 'R':
            state = Status.Running
        elif state in ['E', 'C']:
            state = Status.Complete
        '''
        output_path = job[2]
        error_path = job[2]
        
        if len(output_path.split(":")) == 2:
            output_path = output_path.split(":")[1]
        if len(error_path.split(":")) == 2:
            error_path = error_path.split(":")[1]
        
        env = job[3]
        vars = env.split(',')
        
        working_dir = "~"
        '''
        for v in vars:
            kv = v.split("=")
            if kv[0] == "PBS_O_WORKDIR":
                working_dir = kv[1]
                flag = True
                break
        '''
        job_id = job[4]
        name = job[5]
        user = job[6]
        
        c = ClusterJob(job_id, name, user, state, output_path, error_path, 
            working_dir, exit_code, [])
        
        #get resource manager specific details
        resources_allocated = DataSection("Allocated Resources", [
            DataField(Key='mem', Label="Allocated Memory", ValueType=4, 
                DefaultValue=str(job[7])
            ),
            DataField(Key='nodes', Label="Allocated Nodes", ValueType=4, 
                DefaultValue=str(job[8])
            ),
            DataField(Key='walltime', Label="Allocated Walltime", 
                ValueType=4, DefaultValue=str(job[9])
            ),
            DataField(Key='queue', Label="Queue", ValueType=4, 
                DefaultValue=str(job[10])
            ),
        ])
        
        resources_used = DataSection("Resources Used", [
            DataField(Key='cput', Label="CPUs requested", ValueType=4, 
                DefaultValue=str(job[11])
            ),
            DataField(Key='mem_used', Label="Memory Used", ValueType=4, 
                DefaultValue=str(job[12])
            ),
            DataField(Key='vmem', Label="Disk space used (MB)", ValueType=4, 
                DefaultValue=str(job[13])
            ),
            DataField(Key='walltime_used', Label="Walltime Used", ValueType=4, 
                DefaultValue=str(job[14])
            ),
            DataField(Key='exec_host', Label="Execution Node", ValueType=4, 
                DefaultValue=str(job[15])
            ),
        ])
        
        tempCreatedTime = job[16].replace("T", " ")
        tempStartTime = job[17].replace("T", " ")
        tempMaxTime = job[18].replace("T", " ")
        
        cT = datetime.datetime.strptime(tempCreatedTime, "%Y-%m-%d %H:%M:%S")
        sT = datetime.datetime.strptime(tempStartTime, "%Y-%m-%d %H:%M:%S")
        mT = datetime.datetime.strptime(tempMaxTime, "%Y-%m-%d %H:%M:%S")
        
        epoch = datetime.datetime.fromtimestamp(0)
        
        tempCT = (cT - epoch).total_seconds()
        tempST = (sT - epoch).total_seconds()
        tempMT = (mT - epoch).total_seconds()
        
        time = DataSection("Time", [
            DataField(Key='ctime', Label="Created Time", ValueType=4, 
                DefaultValue=str(tempCT)
            ),
            DataField(Key='start_time', Label="Start Time", ValueType=4, 
                DefaultValue=str(tempST)
            ),
            DataField(Key='comp_time', Label="Max End Time", ValueType=4, 
                DefaultValue=str(tempMT)
            ),
        ])
        
        other = DataSection("Other", [
            DataField(Key='submit_args', Label="Submit Args", ValueType=4, 
                DefaultValue=str(job[19])
            ),
            DataField(Key='Output_Path', Label="Output Log", ValueType=4, 
                DefaultValue=output_path
            ),
            DataField(Key='Error_Path', Label="Error Log", ValueType=4, 
                DefaultValue=error_path
            ),
            DataField(Key='Priority', Label="Priority", ValueType=4, 
                DefaultValue=str(job[20])
            ),
            DataField(Key='Variable_List', Label="Environmental Variables", 
                ValueType=4, DefaultValue=env
            ),
            DataField(Key='comment', Label="Comment", ValueType=4, 
                DefaultValue=str(job[21])
            )
        ])
        
        c.DataSections.append(resources_allocated)
        c.DataSections.append(resources_used)
        c.DataSections.append(time)
        c.DataSections.append(other)
        
        return c
    
    
    def GetSettings(self):
        config = self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol show config')
        
        data_sections = [
            DataSection(
                SectionHeader = "SLURM Settings",
                DataFields = [
                    DataField("ControlMachine", "Server name", ValueType.Label, "", True),
                    DataField("SLURM_VERSION", "SLURM version", ValueType.Label, "", True),
                    DataField("SLURM_CONF", "SLURM config", ValueType.Label, False),
                    DataField("SlurmdUser", "Slurmd user", ValueType.Label, False),
                    #DataField("default_queue", "Default queue", ValueType.Text, ""),
                    DataField("MinJobAge", "Min job age (s)", ValueType.Number, False),
                    #DataField("CompleteWait", "Complete wait (ms)", ValueType.Number, False),
                    #DataField("WaitTime", "Wait time (s)", ValueType.Number, False),
                    DataField("InactiveLimit", "Inactive limit (s)", ValueType.Number, False),
                    DataField("KillWait", "Kill wait (s)", ValueType.Number, False),
                    DataField("MaxJobCount", "Max jobs", ValueType.Number, False),
                    #DataField("SchedulerTimeSlice", "Scheduler time slice (s)", ValueType.Number, False),
                    DataField("SlurmUser", "Slurm user", ValueType.Text, False),
                    DataField("SlurmctldPort", "Slurmctld port", ValueType.Number, False),
                    DataField("SlurmctldTimeout", "Slurmctld timeout (s)", ValueType.Number, False),
                    DataField("SlurmdPort", "Slurmd port", ValueType.Number, False),
                    DataField("SlurmdTimeout", "Slurmd timeout (s)", ValueType.Number, False),
                ]
            )
        ]
        
        settings_section = SettingsSection("SLURM Settings", [])
        
        for line in config.split('\n'):
            # Server details
            if "=" in line:
                setting_line = line.split("=")
                
                setting = setting_line[0].strip()
                value = setting_line[1].strip()
                
                # If the setting is a true or false value, convert the string to an actual boolean 
                '''if setting in ["scheduling", "query_other_jobs", "mom_job_sync", 
                    "moab_array_compatible"]:
                    value = value.lower() == "true"'''
                
                
                if setting in ["SlurmUser", "SlurmdUser"]:
                    s = Setting(Name=setting, Value=value.split("(")[0])
                    settings_section.Settings.append(s)
                    
                if setting in ["ControlMachine", "SLURM_VERSION", "MaxJobCount", "SlurmctldPort", "SlurmdPort", "SLURM_CONF"]:
                    s = Setting(Name=setting, Value=value)
                    settings_section.Settings.append(s)
                    
                # Remove text chars
                if setting in ["KillWait", "SlurmctldTimeout", "SlurmdTimeout", "MinJobAge", "InactiveLimit"]:
                    temp = re.sub(r'\D', "", value)
                    s = Setting(Name=setting, Value=int(temp))
                    settings_section.Settings.append(s)
                # Remove text chars and convert to milliseconds
                '''elif setting in ["TCPTimeout"]:
                    temp = re.sub(r'\D', "", value)
                    s = Setting(Name=setting, Value=int(temp)*1000)
                    settings_section.Settings.append(s)'''
                
        settings = Data(data_sections, [settings_section])
        
        return settings
    

    def UpdateSettings(self, settings_sections):
        output = ""
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()
        	
        for section in settings_sections:
            for setting in section.Settings:
                if setting.Name == "MinJobAge":
                    minJobAge = setting.Value
                elif setting.Name == "InactiveLimit":
                    inactiveLimit = setting.Value
                elif setting.Name == "KillWait":
                    killWait = setting.Value
                elif setting.Name == "MaxJobCount":
                    maxJobCount = setting.Value
                elif setting.Name == "SlurmUser":
                    slurmUser = setting.Value
                elif setting.Name == "SlurmctldPort":
                    slurmctldPort = setting.Value
                elif setting.Name == "SlurmctldTimeout":
                    slurmctldTimeout = setting.Value
                elif setting.Name == "SlurmdPort":
                    slurmdPort = setting.Value
                elif setting.Name == "SlurmdTimeout":
                    slurmdTimeout = setting.Value

        with open(confPath, "w") as f:
            for line in configFile:
                if "MinJobAge" in line:
                    f.write("MinJobAge={0}\n".format(minJobAge))
                elif "InactiveLimit" in line:
                    f.write("InactiveLimit={0}\n".format(inactiveLimit))
                elif "KillWait" in line:
                    f.write("KillWait={0}\n".format(killWait))
                elif "MaxJobCount" in line:
                    f.write("MaxJobCount={0}\n".format(maxJobCount))
                elif "SlurmUser" in line:
                    f.write("SlurmUser={0}\n".format(slurmUser))
                elif "SlurmctldPort" in line:
                    f.write("SlurmctldPort={0}\n".format(slurmctldPort))
                elif "SlurmdPort" in line:
                    f.write("SlurmdPort={0}\n".format(slurmdPort))
                elif "SlurmdTimeout" in line:
                    f.write("SlurmdTimeout={0}\n".format(slurmdTimeout))
                
                else:
                    f.write(line)
        
        self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol reconfigure')
        
        return output

    def GetQueues(self):
        output = self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol show partition -o')
        data = output.splitlines()
        
        #set up the data structure
        data_sections = [
                DataSection(
                    SectionHeader = "General",
                    DataFields = [
                        DataField("Nodes", "Nodes", ValueType.Text, "node-1"),
                        DataField("State", "Enabled", ValueType.Checkbox, False),
                        DataField("Default", "Default", ValueType.Checkbox, False),
                    ]
                ), DataSection(
                    SectionHeader = "User Settings",
                    DataFields = [
                        #DataField("max_user_queuable", "x Max jobs queuable per user", ValueType.Number, 5),
                        #DataField("max_user_run", "x Max jobs running per user", ValueType.Number, 1),
                    ]
                ), DataSection(
                    SectionHeader = "Resources",
                    DataFields = [
                        DataField("TotalNodes", "Total nodes", ValueType.Label, "1"),
                        DataField("TotalCPUs", "Total CPUs", ValueType.Label, "1"),
                        DataField("MaxMemPerNode", "Max memory (mb)", ValueType.Text, "1gb"),
                        DataField("MaxCPUsPerNode", "Max cores", ValueType.Text, "1"),
                        DataField("MaxNodes", "Max nodes", ValueType.Text, "1"),
                        DataField("MaxTime", "Max walltime (hh:mm:ss)", ValueType.Text, "01:00:00"),
                        #DataField("DefMemPerNode", "Default memory (mb)", ValueType.Text, "1gb"),
                        #DataField("resources_default.ncpus", "x Default cores", ValueType.Number, 1),
                        #DataField("resources_default.nodes", "x Default nodes", ValueType.Number, 1),
                    ]
                )
            ]
        
        queues = Data(data_sections, [])
        
        #parse the queue data
        for partitions in data:
            line = partitions.split()
            partitionLine = line[0].split("=")
            
            #queue details
            queue_name = partitionLine[1]
            queue = Queue(QueueName=queue_name, SettingsSections=[
                SettingsSection("General", []), 
                SettingsSection("User Settings", []), 
                SettingsSection("Resources", []), 
                SettingsSection("Access Control", [])
            ])

            s = Setting(Name="AllowGroups", Value=line[1].split("=")[1])
            queue.SettingsSections[3].Settings.append(s)
            s = Setting(Name="AllowAccounts", Value=line[2].split("=")[1])
            queue.SettingsSections[3].Settings.append(s)
            #s = Setting(Name="AllowQos", Value=line[3].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            #s = Setting(Name="AllocNodes", Value=line[4].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="Default", Value=line[5].split("=")[1])
            queue.SettingsSections[0].Settings.append(s)
            #s = Setting(Name="QoS", Value=line[6].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            #s = Setting(Name="DefaultTime", Value=line[7].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="DisableRootJobs", Value=line[8].split("=")[1])#
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="ExclusiveUser", Value=line[9].split("=")[1])#
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="GraceTime", Value=line[10].split("=")[1])#
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="Hidden", Value=line[11].split("=")[1])#
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="MaxNodes", Value=line[12].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="MaxTime", Value=line[13].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            #s = Setting(Name="MinNodes", Value=line[14].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            #s = Setting(Name="LLN", Value=line[15].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="MaxCPUsPerNode", Value=line[16].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="Nodes", Value=line[17].split("=")[1])
            queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="PriorityJobFactor", Value=line[18].split("=")[1])#
            queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="PriorityTier", Value=line[19].split("=")[1])#
            queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="RootOnly", Value=line[20].split("=")[1])#
            queue.SettingsSections[0].Settings.append(s)
            #s = Setting(Name="ReqResv", Value=line[21].split("=")[1])
            #queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="OverSubscribe", Value=line[22].split("=")[1])#
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="PreemptMode", Value=line[23].split("=")[1])#
            queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="State", Value=line[24].split("=")[1])#bug
            queue.SettingsSections[0].Settings.append(s)
            s = Setting(Name="TotalCPUs", Value=line[25].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="TotalNodes", Value=line[26].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="SelectTypeParameters", Value=line[27].split("=")[1])#
            queue.SettingsSections[0].Settings.append(s)
            #s = Setting(Name="DefMemPerNode", Value=line[28].split("=")[1])
            #queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="MaxMemPerNode", Value=line[29].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)

            queues.Data.append(queue)
        return queues
    
    def AddQueue(self, queue_name):
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()
        
        with open(confPath, "w") as f:
            for line in configFile:
                f.write(line)
                if "# PARTITIONS" in line:
                    f.write("PartitionName={0}\n".format(queue_name))
                    
        self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol reconfigure')
    
    def UpdateQueue(self, queue):
        output = ""
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()
        	
        for section in queue.SettingsSections:
            for setting in section.Settings:
                if setting.Name == "Nodes":
                    nodes = setting.Value
                elif setting.Name == "Default":
                    default = setting.Value
                elif setting.Name == "MaxTime":
                    maxTime = setting.Value
                elif setting.Name == "MaxMemPerNode":
                    maxMem = setting.Value
                elif setting.Name == "MaxCPUsPerNode":
                    maxCPUs = setting.Value
                #elif setting.Name == "DefMemPerNode":
                #    defaultMem = setting.Value
                elif setting.Name == "State":
                    state = setting.Value

        with open(confPath , "w") as f:
            for line in configFile:
                if queue.QueueName in line:
                    if nodes in "(null)":
                        f.write("PartitionName={0} Default={1} MaxTime={2} MaxMemPerNode={3} MaxCPUsPerNode={4} State={5}\n".format(queue.QueueName, default, maxTime, maxMem, maxCPUs, state))
                    else:
                        f.write("PartitionName={0} Nodes={1} Default={2} MaxTime={3} MaxMemPerNode={4} MaxCPUsPerNode={5} State={6}\n".format(queue.QueueName, nodes, default, maxTime, maxMem, maxCPUs, state))
                else:
                    f.write(line)
        
        self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol reconfigure')

        return output
    
    
    def DeleteQueue(self, queue_name):
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()
        	
        with open(confPath , "w") as f:
            for line in configFile:
                if queue_name not in line:
                    f.write(line)
        #output = self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol delete PartitionName=%s' % (queue_name))
        self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol reconfigure')

    def GetNodes(self):
        nodes = []
        
        try:
            out = self.RunUserProcess('/mounts/rey/software/slurm/bin/sinfo -N -o "%N %t %C %f"')
            data = out.splitlines()
            nodeDict = {'name': 'node', 'state': 'down', 'busy_cores': 0, 'free_cores': 1, 'num_cores': 1, 'properties': 'test node'}
            
            for node in data:
                line = node.split()
                
                if "ODELIST" not in line[0]:
                    # Don't allow nodes to be added twice, as "sinfo -N" returns a node for each partition
                    if line[0] not in nodeDict['name']:
                        nodeDict['name'] = line[0]
                        
                        if "down" in line[1] or "unk" in line[1]:
                            nodeDict['state'] = "down"
                        else:
                            nodeDict['state'] = line[1]
                        
                        cpu = line[2].split("/")
                        nodeDict['busy_cores'] = int(cpu[0])
                        nodeDict['free_cores'] = int(cpu[1])
                        #nodeDict['free_cores'] = int(cpu[2])
                        nodeDict['num_cores'] = int(cpu[3])
                        
                        nodeDict['properties'] = line[3]
                    
                        n = Node(nodeDict['name'], nodeDict['state'], nodeDict['num_cores'], nodeDict['busy_cores'], nodeDict['free_cores'], nodeDict['properties'])
                        
                        nodes.append(n)

        except Exception, ex:
            f = open('/tmp/nodes.txt', 'w')
            print >> f, str(ex)
            f.close()
        
        return nodes
    

    def AddNode(self, node):
        raise NotImplementedError
        # must be added directly to slurm.conf
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()
        
        with open(confPath + ".new", "w") as f:
            for line in configFile:
                f.write(line)
                if "# slave node" in line:
                    f.write("NodeName={0} CPUs={1} NodeAddr={2} Port={3} State=UNKNOWN\n".format(node.name, node.num_cores, node.other.split(":")[0], node.other.split(":")[1]))
        
        #self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol reconfigure')
    

    def UpdateNode(self, node):
        raise NotImplementedError
        # must be modified directly in slurm.conf
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()

        with open(confPath + ".new", "w") as f:
            for line in configFile:
                f.write(line)
                if line in ["NodeName={0}".format(node.name)]:
                    f.write("wut")
                    #f.write("NodeName={0} CPUs={1} Feature={2}".format(node.name, node.num_cores, node.other))
    
    
    def DeleteNode(self, id):
        raise NotImplementedError
        # must be deleted directly from slurm.conf
        confPath = "/mounts/rey/software/slurm/etc/slurm.conf"
        
        with open(confPath) as f:
        	configFile = f.readlines()

        with open(confPath + ".new", "w") as f:
            for line in configFile:
                f.write(line)
                if line in ["NodeName={0}".format(node.name)]:
                    f.write("wut")
                    #f.write("NodeName={0} CPUs={1} Feature={2}".format(node.name, node.num_cores, node.other))
    
    
    def GetDefaultResources(self):
        return DataSection("slurm", [
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
                Label = "Memory (mb)",
                ValueType = ValueType.Number,
                DefaultValue = 1000,
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
    
    
    def CreateJobScript(self, job_name, job_dir, script_name, output_log, error_log, settings, has_dependencies, commands):
        script = os.path.join(job_dir, script_name)
        
        with open(script, 'w') as job_script:
            print >> job_script, "#!/bin/bash"

            print >> job_script, "#SBATCH -J %s" % job_name
            print >> job_script, "#SBATCH -o %s" % output_log
            print >> job_script, "#SBATCH -e %s" % error_log
            print >> job_script, "#SBATCH -D %s" % job_dir
            
            nodes = ""
            for setting in settings:
                if setting.Name == "nodes":
                    nodes += "#SBATCH -N %s" % setting.Value
                elif setting.Name == "ppn":#Cores
                    print >> job_script, "#SBATCH -n %s" % setting.Value
                #elif setting.Name == "mem":
                #    print >> job_script, "#SBATCH --mem=%s" % setting.Value
                elif setting.Name == "walltime":
                    print >> job_script, "#SBATCH -t %s" % setting.Value
                elif setting.Name == "queue":
                    print >> job_script, "#SBATCH -p %s" % setting.Value
                elif setting.Name == "variables":
                    if setting.Value.strip() != "":
                        print >> job_script, "#SBATCH --export=%s" % setting.Value
                    #else:
                    #    print >> job_script, "#SBATCH -V"
            print >> job_script, nodes 
            
            #has_dependencies?
            if has_dependencies:
                print >> job_script, "#SBATCH -d"
            
            print >> job_script, ""
            print >> job_script, commands
            
        
        return script
    
    
    def ExecuteJobScript(self, script):
        '''temp = script.splitlines()
        jobSript = temp[0]
        
        with open("/tmp/debug.txt", "w") as f: #debugging
        	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
        	f.write(jobSript + "\n")'''
	
        return self.RunUserProcess("/mounts/rey/software/slurm/bin/sbatch %s" % script)

    def HoldJob(self, id):
        return self.RunUserProcess("/mounts/rey/software/slurm/bin/scontrol suspend %s" % id)

    def ReleaseJob(self, id):
        return self.RunUserProcess("/mounts/rey/software/slurm/bin/scontrol resume %s" % id)
    
    def KillJob(self, id):
        debug = self.RunUserProcess("/mounts/rey/software/slurm/bin/scancel %s" % id)
        return debug

    