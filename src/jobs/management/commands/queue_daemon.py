from django.core.management.base import BaseCommand  
from django import db

from jobs.JMS import JobManager

import sys, time, subprocess, traceback
from lxml import objectify

from utilities.services.daemon import Daemon
from utilities.io.filesystem import File

class QueueDaemon(Daemon):
    def run(self):
        with open("/tmp/queue-daemon.txt", 'w') as f:
            try:
                count = 1
                jms = JobManager()
            
                while True:
                    try:
                        f.write("\r" + str(count))
                        f.flush()
                        
                        count += 1
                        jms.UpdateJobHistory()
                        
                    except Exception, err:
                        # Reset database connection to avoid "MySQL has gone away" error after daemon has been running for a long time    
                        db.close_connection() 
                        f.write("Inner Error: " + str(err))
                    
                    time.sleep(5)
            except Exception, err:
                f.write("Outer Error: " + str(err))

                       
class Command(BaseCommand):

    help = "Usage: python manage.py queue_daemon [start|restart|stop]"

    def handle(self, *args, **options):
        daemon = QueueDaemon('/tmp/queue-daemon.pid')
        
        if args[0] == 'start':
            daemon.start()
        elif args[0] == 'restart':
            daemon.restart()
        elif args[0] == 'stop':
            daemon.stop()       

