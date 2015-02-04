from django.core.management.base import NoArgsCommand, make_option

from job.JMS import JMS
from django.db import transaction

import sys, time, subprocess
from lxml import objectify
from daemon import Daemon


class QueueDaemon(Daemon):
    def run(self):
        count = 1
        while True:
            with open("/tmp/queue-daemon.txt", "w") as f:
                print >> f, str(count)
                count += 1
                
                try:
                    process = subprocess.Popen("qstat -x", shell=True, stdout=subprocess.PIPE)
                    out, err = process.communicate()
                    
                    data = objectify.fromstring(out)
                    
                    jms = JMS() 
                    for job in data.Job:
                        print >> f, job.Job_Id
                        jms.AddUpdateClusterJob(job)
                          
                except Exception, err:
                    print >> f, "Error: " + str(err)
                  
            time.sleep(5)

                       
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

