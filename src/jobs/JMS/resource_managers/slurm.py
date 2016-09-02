from base import *
from objects import *

import os, sys, datetime, socket, re

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
<<<<<<< HEAD
        out = self.RunUserProcess('/mounts/rey/software/slurm/bin/squeue -j {0} -o "%r %t %Z %r %F %j %u %m %D %l %P %C N/A %d %M %B %V %S %e %o %p %k"'.format(id) )
=======
        out = self.RunUserProcess('/mounts/rey/software/slurm/bin/squeue -j {0} -o "%r %t %Z %r %F %j %u"'.format(id) )
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        data = out.splitlines()
        return self._ParseJob(data[1])


    def _ParseJob(self, data):
        job = data.strip().split()
<<<<<<< HEAD
	
=======
        
        	
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        #get core details to update JobStage
        exit_code = job[0]
        state = job[1]
        if state == 'H':
            state = Status.Held
        elif state == 'Q':
            state = Status.Queued
        elif state == 'R':
            state = Status.Running
        elif state in ['E', 'C']:
            state = Status.Complete
        
        output_path = job[2]
        error_path = job[2]
        
        if len(output_path.split(":")) == 2:
            output_path = output_path.split(":")[1]
        if len(error_path.split(":")) == 2:
            error_path = error_path.split(":")[1]
        
        env = job[3]
        vars = env.split(',')
        
        working_dir = "~"
        for v in vars:
            kv = v.split("=")
            if kv[0] == "PBS_O_WORKDIR":
                working_dir = kv[1]
                flag = True
                break
        
        job_id = job[4]
        name = job[5]
        user = job[6]
        
        c = ClusterJob(job_id, name, user, state, output_path, error_path, 
            working_dir, exit_code, [])
        
        #get resource manager specific details
<<<<<<< HEAD
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
=======
        '''
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
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
            ),
        ])
        
        resources_used = DataSection("Resources Used", [
<<<<<<< HEAD
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
        
        time = DataSection("Time", [
            DataField(Key='ctime', Label="Created Time", ValueType=4, 
                DefaultValue=str(job[16])
            ),
            DataField(Key='start_time', Label="Start Time", ValueType=4, 
                DefaultValue=str(job[17])
            ),
            DataField(Key='comp_time', Label="Completed Time", ValueType=4, 
                DefaultValue=str(job[18])
            ),
        ])
        
        other = DataSection("Other", [
            DataField(Key='submit_args', Label="Submit Args", ValueType=4, 
                DefaultValue=str(job[19])
=======
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
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
            ),
            DataField(Key='Output_Path', Label="Output Log", ValueType=4, 
                DefaultValue=output_path
            ),
            DataField(Key='Error_Path', Label="Error Log", ValueType=4, 
                DefaultValue=error_path
            ),
            DataField(Key='Priority', Label="Priority", ValueType=4, 
<<<<<<< HEAD
                DefaultValue=str(job[20])
=======
                DefaultValue=str(GetAttr(job, 'Priority', 'n/a'))
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
            ),
            DataField(Key='Variable_List', Label="Environmental Variables", 
                ValueType=4, DefaultValue=env
            ),
            DataField(Key='comment', Label="Comment", ValueType=4, 
<<<<<<< HEAD
                DefaultValue=str(job[21])
            )
        ])
        
        c.DataSections.append(resources_allocated)
        c.DataSections.append(resources_used)
        c.DataSections.append(time)
        c.DataSections.append(other)
=======
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
        ])'''
        
        #c.DataSections.append(resources_allocated)
        #c.DataSections.append(resources_used)
        #c.DataSections.append(time)
        #c.DataSections.append(other)
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        
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
<<<<<<< HEAD
                    DataField("SlurmdUser", "Slurmd user", ValueType.Label, False),
                    #DataField("default_queue", "Default queue", ValueType.Text, ""),
                    DataField("MinJobAge", "Min job age (s)", ValueType.Number, False),
                    #DataField("CompleteWait", "Complete wait (ms)", ValueType.Number, False),
                    #DataField("WaitTime", "Wait time (s)", ValueType.Number, False),
                    DataField("InactiveLimit", "Inactive limit (s)", ValueType.Number, False),
                    DataField("KillWait", "Kill wait (s)", ValueType.Number, False),
                    DataField("MaxJobCount", "Max jobs", ValueType.Number, False),
                    #DataField("SchedulerTimeSlice", "Scheduler time slice (s)", ValueType.Number, False),
=======
                    #DataField("default_queue", "Default queue", ValueType.Text, ""),
                    DataField("BatchStartTimeout", "Batch start timeout (ms)", ValueType.Number, False),
                    DataField("CompleteWait", "Complete wait (ms)", ValueType.Number, False),
                    DataField("GetEnvTimeout", "Get Env timeout (ms)", ValueType.Number, False),
                    DataField("TCPTimeout", "TCP timeout (ms)", ValueType.Number, False),
                    DataField("KillWait", "Kill wait (s)", ValueType.Number, False),
                    DataField("MaxJobCount", "Max jobs", ValueType.Number, False),
                    DataField("SchedulerTimeSlice", "Scheduler time slice (s)", ValueType.Number, False),
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
                    DataField("SlurmUser", "Slurm user", ValueType.Text, False),
                    DataField("SlurmctldPort", "Slurmctld port", ValueType.Number, False),
                    DataField("SlurmctldTimeout", "Slurmctld timeout (s)", ValueType.Number, False),
                    DataField("SlurmdPort", "Slurmd port", ValueType.Number, False),
                    DataField("SlurmdTimeout", "Slurmd timeout (s)", ValueType.Number, False),
<<<<<<< HEAD
=======
                    DataField("SlurmdUser", "Slurmd user", ValueType.Text, False)
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
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
                
                if setting in ["ControlMachine", "SLURM_VERSION", "MaxJobCount", "SlurmUser", "SlurmctldPort", "SlurmdPort", "SlurmdUser", "SLURM_CONF"]:
                    s = Setting(Name=setting, Value=value)
                    settings_section.Settings.append(s)
                    
                # Remove text chars
<<<<<<< HEAD
                if setting in ["KillWait", "SlurmctldTimeout", "SlurmdTimeout", "MinJobAge", "InactiveLimit"]:
=======
                if setting in ["KillWait", "SchedulerTimeSlice", "SlurmctldTimeout", "SlurmdTimeout"]:
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
                    temp = re.sub(r'\D', "", value)
                    s = Setting(Name=setting, Value=int(temp))
                    settings_section.Settings.append(s)
                # Remove text chars and convert to milliseconds
<<<<<<< HEAD
                '''elif setting in ["TCPTimeout"]:
                    temp = re.sub(r'\D', "", value)
                    s = Setting(Name=setting, Value=int(temp)*1000)
                    settings_section.Settings.append(s)'''
=======
                elif setting in ["TCPTimeout", "BatchStartTimeout", "CompleteWait", "GetEnvTimeout"]:
                    temp = re.sub(r'\D', "", value)
                    s = Setting(Name=setting, Value=int(temp)*1000)
                    settings_section.Settings.append(s)
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
                
        settings = Data(data_sections, [settings_section])
        
        return settings
    
<<<<<<< HEAD
    def UpdateSettings(self, settings_sections):#duplicate entries to file, probably simple logic oversight
        with open(settings_sections[0].Settings[2].Value) as f:
        	configFile = f.readlines()
        	
        #self.RunUserProcess("mv {0} {0}.old".format(settings_sections[0].Settings[2].Value))
        
        with open(settings_sections[0].Settings[2].Value + ".new", "a") as f:
            for line in configFile:
                edit = False
                for section in settings_sections:
                    for setting in section.Settings:
                        if setting.Name == line.split("=")[0]:
                            f.write(setting.Name + "=" + str(setting.Value) + "\n")
                            edit = False
                            
                        else:
                            edit = True
                if edit:
                    f.write(line)
            	
        '''
        with open("/tmp/debug.txt", "w") as f: #debugging
        	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
        	f.write(str(configFile[4].split("=")[0]) + "\n")

        	if configFile[4].split("=")[0] in settings_sections[0].Settings:
        	    f.write("true" + "\n")
        	else:
        	    f.write(settings_sections[0].Settings[2].Value + "\n")
        '''
            
        output = ""
        #for section in settings_sections:
        #    for setting in section.Settings:
                # Duplicate and update .conf file for lack of a better config update command

                #output += self.RunUserProcess('qmgr -c "set server %s = %s"' % (setting.Name, str(setting.Value)))

        #self.RunUserProcess("cp /mounts/rey/software/slurm/etc/slurm.conf /mounts/rey/software/slurm/etc/slurm.conf.old".format(settings_sections[0].Settings[2].Value))
        #self.RunUserProcess("/mounts/rey/software/slurm/bin/scontrol reconfigure") # Must be run as SLURM user
=======
    def UpdateSettings(self, settings_sections):
        
        output = ""
        for section in settings_sections:
            for setting in section.Settings:
                with open("/tmp/debug.txt", "w") as f: #debugging
                	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
                	f.write(str(setting.Name) + "\n")
                #output += "debug"#self.RunUserProcess('qmgr -c "set server %s = %s"' % (setting.Name, str(setting.Value)))
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
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
                        DataField("MaxMemPerNode", "Max memory", ValueType.Text, "1gb"),
                        DataField("MaxCPUsPerNode", "Max cores", ValueType.Text, "1"),
                        DataField("MaxNodes", "Max nodes", ValueType.Text, "1"),
                        DataField("MaxTime", "Max walltime", ValueType.Text, "01:00:00"),
                        DataField("DefMemPerNode", "Default memory", ValueType.Text, "1gb"),
                        #DataField("resources_default.ncpus", "x Default cores", ValueType.Number, 1),
                        #DataField("resources_default.nodes", "x Default nodes", ValueType.Number, 1),
                        DataField("DefaultTime", "Default walltime", ValueType.Text, "01:00:00"),
                    ]
                ), DataSection(
                    SectionHeader = "Access Control",
                    DataFields = [
                        #DataField("group_enable", "x Enable group-based access control?", ValueType.Checkbox, False),
                        #DataField("user_enable", "x Enable user-based access control?", ValueType.Checkbox, False),
                        DataField("AllowGroups", "Groups with access", ValueType.Text, ""),
                        DataField("AllowAccounts", "Users with access", ValueType.Text, "")
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
            s = Setting(Name="DefMemPerNode", Value=line[28].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)
            s = Setting(Name="MaxMemPerNode", Value=line[29].split("=")[1])
            queue.SettingsSections[2].Settings.append(s)

            queues.Data.append(queue)
        return queues
    
<<<<<<< HEAD
    def AddQueue(self, queue_name): #sudo not working
        #raise NotImplementedError
        output = self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol create PartitionName=%s"' % queue_name, sudo=True)
=======
    def AddQueue(self, queue_name):
        output = "debug"#self.RunUserProcess('qmgr -c "create queue %s"' % queue_name)
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
    
    
    def UpdateQueue(self, queue):
        
<<<<<<< HEAD
        with open("/tmp/debug.txt", "w") as f: #debugging
        	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
        	f.write(queue + "\n")
        
        raise NotImplementedError
	    
        output = ""
=======
	
        '''output = ""
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        max_nodes = 1
        max_procs = 1
        def_nodes = 1
        def_procs = 1
        
        for section in queue.SettingsSections:
            for setting in section.Settings:
                print >> f, setting.Name, setting.Value
                #set access controls - values come as csv
                if setting.Name in ["acl_groups", "acl_users"]:
                    values = setting.Value.split(",")
                    if len(values) == 1 and values[0] == "":
                        #remove all users
                        output += "debug"#self.RunUserProcess('qmgr -c "set queue %s %s = temp"' % (queue.QueueName, setting.Name))
                        output += "debug"#self.RunUserProcess('qmgr -c "set queue %s %s -= temp"' % (queue.QueueName, setting.Name))
                    else:
                        for index, value in enumerate(values):
                            value = value.strip()
                            if index == 0:
                                output += "debug"#self.RunUserProcess('qmgr -c "set queue %s %s = %s"' % (queue.QueueName, setting.Name, value))
                            else:
                                output += "debug"#self.RunUserProcess('qmgr -c "set queue %s %s += %s"' % (queue.QueueName, setting.Name, value))
                elif setting.Name == "resources_max.nodes":
                    max_nodes = setting.Value
                elif setting.Name == "resources_max.ncpus":
                    max_procs = setting.Value
                elif setting.Name == "resources_default.nodes":
                    def_nodes = setting.Value
                elif setting.Name == "resources_default.ncpus":
                    def_procs = setting.Value
                
                output += "debug"#self.RunUserProcess('qmgr -c "set queue %s %s = %s"' % (queue.QueueName, setting.Name, str(setting.Value)))
        
        output += "debug"#self.RunUserProcess('qmgr -c "set queue %s resources_max.nodes = %s:ppn=%s"' % (queue.QueueName, str(max_nodes), str(max_procs)))
        output += "debug"#self.RunUserProcess('qmgr -c "set queue %s resources_default.nodes = %s:ppn=%s"' % (queue.QueueName, def_nodes, def_procs))
<<<<<<< HEAD
        
        #output += self.RunUserProcess('/mounts/rey/software/slurm/bin/scontrol create PartitionName=%s" ' % (queue.QueueName, def_nodes, def_procs))
        
        return output
    
    
    def DeleteQueue(self, queue_name):
        raise NotImplementedError
        output = "debug"#self.RunUserProcess('qmgr -c "delete queue %s"' % queue_name)

    def GetAdministrators(self):
        raise NotImplementedError
=======
        '''
        return output
    
    
    def DeleteQueue(self, queue_name):       
        output = "debug"#self.RunUserProcess('qmgr -c "delete queue %s"' % queue_name)

    def GetAdministrators(self):
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#self.RunUserProcess('qmgr -c "print server"', expect=self.user.username + "@%s:" % socket.gethostname())
        
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
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#self.RunUserProcess('qmgr -c "set server managers += %s"' % (administrator_name))
        output += "debug"#self.RunUserProcess('qmgr -c "set server operators += %s"' % (administrator_name))
        return output
    
    
    def UpdateAdministrator(self, administrator):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = ""
        for section in administrator.SettingsSections:
            for setting in section.Settings:
                if setting.Value:
                    output += "debug"#"\n" + self.RunUserProcess('qmgr -c "set server %s += %s"' % (setting.Name, administrator.AdministratorName))
                else:
                    output += "debug"#"\n" + self.RunUserProcess('qmgr -c "set server %s -= %s"' % (setting.Name, administrator.AdministratorName))
        return output
    
    
    def DeleteAdministrator(self, administrator_name):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#"\n" + self.RunUserProcess('qmgr -c "set server managers -= %s"' % administrator_name)
        output += "debug"#"\n" + self.RunUserProcess('qmgr -c "set server operators -= %s"' % administrator_name)
        return output

    
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
    
<<<<<<< HEAD
    
    def AddNode(self, node):
        raise NotImplementedError
=======
    def AddNode(self, node):
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#self.RunUserProcess('qmgr -c "create node %s"' % node.name)   
        self.UpdateNode(node)
    
    
<<<<<<< HEAD
    def UpdateNode(self, node):
        raise NotImplementedError
=======
    def UpdateNode(self, node):    
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#self.RunUserProcess('qmgr -c "set node %s np = %s"' % (node.name, str(node.num_cores)))
        output += "debug"#self.RunUserProcess('qmgr -c "set node %s properties = %s"' % (node.name, node.other))
    
    
    def DeleteNode(self, id):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = "debug"#self.RunUserProcess('qmgr -c "delete node %s"' % id) 
    
    
    def Stop(self):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        return "debug"#self.RunUserProcess("qterm -t quick")
    
    
    def Start(self):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        return "debug"#self.RunUserProcess("qserverd", sudo=True)
    
    
    def Restart(self):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        output = self.Stop()
        output += self.Start()
        return output
    
    
    def GetDefaultResources(self):
<<<<<<< HEAD
        raise NotImplementedError
=======
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
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

    
    def CreateJobScript(self, job_name, job_dir, script_name, output_log, error_log, settings, has_dependencies, commands):
<<<<<<< HEAD
        raise NotImplementedError
=======
        
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
        script = os.path.join(job_dir, script_name)
        
        with open(script, 'w') as job_script:
            print >> job_script, "#!/bin/sh"
            print >> job_script, "#PBS -o localhost:%s" % output_log
            print >> job_script, "#PBS -e localhost:%s" % error_log
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
            
            #has_dependencies?
            if has_dependencies:
                print >> job_script, "#PBS -h"
            
            print >> job_script, ""
            print >> job_script, commands   
<<<<<<< HEAD
        
        return script
    
    
    def ExecuteJobScript(self, script):
        raise NotImplementedError
        return "debug"#self.RunUserProcess("qsub %s" % script)
    
    
    def HoldJob(self, id):
        raise NotImplementedError
        return "debug"#self.RunUserProcess("qhold %s" % id)
    
    
    def ReleaseJob(self, id):
        raise NotImplementedError
        return "debug"#self.RunUserProcess("qrls %s" % id)
    
    def KillJob(self, id): #may need sudo?
        debug = self.RunUserProcess("/mounts/rey/software/slurm/bin/scancel %s" % id)
        
        with open("/tmp/debug.txt", "w") as f: #debugging
        	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
        	f.write(debug + "\n")
        
        return debug
    
=======
        
        return script
    
    
    def ExecuteJobScript(self, script):
        return "debug"#self.RunUserProcess("qsub %s" % script)
    
    
    def HoldJob(self, id):
        return "debug"#self.RunUserProcess("qhold %s" % id)
    
    
    def ReleaseJob(self, id):
        return "debug"#self.RunUserProcess("qrls %s" % id)
    
    def KillJob(self, id):
        debug = self.RunUserProcess("/mounts/rey/software/slurm/bin/scancel %s" % id)
        
        with open("/tmp/debug.txt", "w") as f: #debugging
        	f.write(str(datetime.datetime.now()) + " " + os.path.basename(__file__) + "\n")
        	f.write(debug + "\n")
        
        return debug
    
>>>>>>> b1993c7d2c93e11e2273c055cc352b9dc1fc78ab
    def AlterJob(self, Key, Value):
        raise NotImplementedError
        
    