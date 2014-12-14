from django.core.management.base import NoArgsCommand, make_option

from job.JMS import JMS
from django.db import transaction

import sys, time, subprocess
from daemon import Daemon


def UpdateJobHistory():
    with open("/tmp/qd.log", 'w') as f:
        cmd = "qstat -a"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        
        jms = JMS()
        lines = out.splitlines()
        count = 0
        for line in lines:
            print >> f, str(count)
            print >> f, line
            if count > 4 and len(line) > 0:
                job_id = line[0:23].strip()
                print >> f, job_id
                username = line[24:35].strip()
                print >> f, username
                if jms.AddUpdateClusterJob(job_id, username) == False:
                    print >> f, "Failed to add job %s to job history." % job_id
        
            count += 1


class QueueDaemon(Daemon):
    def run(self):
        count = 1
        while True:
            with open("/tmp/queue-daemon.txt", "w") as f:
                print >> f, str(count)
                count += 1
                
                try:
                    UpdateJobHistory()
                except Exception, err:
                    print >> f, str(err)
                  
            time.sleep(15)

                       
class Command(NoArgsCommand):

    help = "Usage: python manage.py queue_daemon"

    option_list = NoArgsCommand.option_list + (
        make_option('--verbose', action='store_true'),
        make_option('--start', action='store_true'),
        make_option('--restart', action='store_true'),
        make_option('--stop', action='store_true'),
    )

    def handle_noargs(self, **options):           
        
        daemon = QueueDaemon('/tmp/queue-daemon.pid')
        
        if options["start"]:
            daemon.start()
        elif options["restart"]:
            daemon.restart()
        elif options["stop"]:
            daemon.stop()       

