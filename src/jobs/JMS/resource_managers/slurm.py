from base import *
from objects import *

import os, sys, datetime

class slurm(BaseResourceManager):
    
    def GetQueue(self):
        column_names = ["Job ID", "Username", "Queue", "Job Name", "State", "Nodes", "Cores", "Time Requested", "Time Used"]
        rows = []
        
        queue = JobQueue(column_names, rows)
        
        
        try:
            out = self.RunUserProcess('/mounts/rey/software/slurm/bin/squeue -o "%F %u %P %j %T %R %C %l %M"')
            #data = objectify.fromstring(out)
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
                nodes = line[5]
                cores = line[6]
                time_requested = line[7]
                time_used = line[8]
                
                row = [
                    str(user),
                    str(partition),
                    str(job_name),
                    str(state),
                    nodes,
                    cores,
                    str(time_requested),
                    time_used
                ]
        
                queue.rows.append(QueueRow(str(job_id), state, row))
            
        return queue
    
    def GetNodes(self):
        nodes = []
        
        try:
            out = self.RunUserProcess('/mounts/rey/software/slurm/bin/sinfo -N -o "%N %t %C %f"')
            #data = objectify.fromstring(out)
            data = out.splitlines()
            
            for node in data:
                line = node.split()
                
                if "ODELIST" not in line[0]:
                    
                    name = line[0]
                    state = line[1]
                    
                    cpu = line[2].split("/")
                    busy_cores = int(cpu[0])
                    free_cores = int(cpu[1])
                    #other_cores = int(cpu[2])
                    num_cores = int(cpu[3])

                    properties=line[3]
                    
                    n = Node(name, state, num_cores, busy_cores, free_cores, properties)
                    
                    nodes.append(n)
            
        except Exception, ex:
            f = open('/tmp/nodes.txt', 'w')
            print >> f, str(ex)
            f.close()
        
        return nodes
        
    
    