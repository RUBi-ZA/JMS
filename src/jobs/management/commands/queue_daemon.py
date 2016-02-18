from django.core.management.base import BaseCommand  
from django.core.mail import EmailMessage
from django.conf import settings
from django import db


from jobs.JMS import JobManager

import sys, time, subprocess, traceback, os, json
from lxml import objectify
from requests import Request, Session

from utilities.services.daemon import Daemon
from utilities.io.filesystem import File

from Queue import Queue
from threading import Thread


class NotificationStatus:
    Success = 1
    Error = 2


def SendEmailNotification(job, num_retries):
    
    if job.EmailStatusID != NotificationStatus.Success:
        status = NotificationStatus.Error
        
        for i in range(num_retries):
            try:
                email = EmailMessage('Job completed - %s' % job.JobName, "",
                    'jms.rubi@outlook.com', #from
                    [job.NotificationEmail], #to
                    ['davidbrownza@outlook.com',], #bcc 
                )
                
                job_report =  "JOB REPORT\n"
                job_report += "---------------------------------------------\n\n"
                job_report += "Job Name: %s\n" % job.JobName
                job_report += "Description: %s\n" % job.JobDescription
                
                if job.JobTypeID == 1:
                    job_report += "Job Type: Custom Job\n"
                elif job.JobTypeID == 2:
                    job_report += "Job Type: Tool\n"
                elif job.JobTypeID == 3:
                    job_report += "Job Type: Workflow\n"
                elif job.JobTypeID == 4:
                    job_report += "Job Type: External\n"
                
                if job.JobTypeID != 3:
                    jobstage = job.JobStages.all()[0]
                    job_report += "\nCluster Job ID: %s\n" % jobstage.ClusterJobID
                    job_report += "Status: %s\n" % jobstage.Status.StatusName
                    job_report += "Exit Code: %s\n" % jobstage.ExitCode
                    job_report += "Working Directory: %s\n" % jobstage.WorkingDirectory
                    job_report += "Output Log: %s (attached)\n" % jobstage.OutputLog
                    job_report += "Error Log: %s (attached)\n" % jobstage.ErrorLog
                    
                    email.attach_file(jobstage.OutputLog)
                    email.attach_file(jobstage.ErrorLog)
                
                else:
                    for jobstage in job.JobStages.all():
                        job_report += "STAGE: %s" % jobstage.Stage.ToolVersion.Tool.ToolName
                        job_report += "Cluster Job ID: %s\n" % jobstage.ClusterJobID
                        job_report += "Status: %s\n" % jobstage.Status.StatusName
                        job_report += "Exit Code: %s\n" % jobstage.ExitCode
                        job_report += "Working Directory: %s\n" % jobstage.WorkingDirectory
                        job_report += "Output Log: %s (attached)\n" % jobstage.OutputLog
                        job_report += "Error Log: %s (attached)\n" % jobstage.ErrorLog
                
                email.body = job_report
                
                #Send notification email
                email.send()
                status = NotificationStatus.Success
                break
            
            except Exception, ex:
                with open("/tmp/email_%s.txt" % job.JobName, 'w') as f:
                    print >> f, traceback.format_exc()
        
        job.EmailStatusID = status
        job.save()
        
    return 0


def SendHTTPNotification(job, num_retries):
    status = NotificationStatus.Error
    
    for i in range(num_retries):
        try:
            s = Session()
            
            if job.JobTypeID != 3:
                jobstage = job.JobStages.all()[0]
                status_id = jobstage.Status.StatusID
                exit_code = jobstage.ExitCode
                
            else:
                status_id = 4
                exit_code = 0
                for jobstage in job.JobStages.all():
                    if jobstage.Status.StatusID == 7:
                        status_id = 7
                        exit_code = 1
                        break
            
            data = { 
                "StatusID": status_id, 
                "ExitCode":  exit_code
            }            
                
                
            if job.NotificationMethod.upper() == "GET" or job.NotificationMethod.upper() == "DELETE":
                req = Request(job.NotificationMethod.upper(), job.NotificationURL,
                    params = data
                )
            else:
                req = Request(job.NotificationMethod.upper(), job.NotificationURL,
                    data = json.dumps(data)
                )
                
            prepped = req.prepare()
            
            response = s.send(prepped)
            if response.status_code == 200:
                status = NotificationStatus.Success
                break
            else:
                with open("/tmp/http_%s.txt" % job.JobName, 'w') as f:
                    print >> f, response.text
            
        except Exception, ex:
            with open("/tmp/http_%s.txt" % job.JobName, 'w') as f:
                print >> f, traceback.format_exc()
        
    job.HttpStatusID = status
    job.save()
    
    return 0


def email_worker(q):
    while True:
        try:
            job = q.get()
            SendEmailNotification(job, 5)
            q.task_done()
        except Exception, ex:
            with open("/tmp/email.txt", 'w') as f:
                print >> f, traceback.format_exc()


def http_worker(q):
    while True:
        job = q.get()
        SendHTTPNotification(job, 5)
        q.task_done()


class QueueDaemon(Daemon):
    def run(self):
        try:
            # Create notification queues
            email_queue = Queue(maxsize=0)
            http_queue = Queue(maxsize=0)
            
            # Spawn email notification threads
            email_thread = Thread(target=email_worker, args=(email_queue,))
            email_thread.setDaemon(True)
            email_thread.start()
            
            # Spawn http notification threads
            http_thread = Thread(target=http_worker, args=(http_queue,))
            http_thread.setDaemon(True)
            http_thread.start()
            
            count = 1
            jms = JobManager()
        
            while True:
                try:
                    # Reset database connection to avoid "MySQL has gone away" error after daemon has been running for a long time   
                    if count % 500 == 0: 
                        db.close_connection()
                    
                    # Update job history and get notifications
                    count += 1
                    emails, http = jms.UpdateJobHistory()
                    
                    # Add notifications to respective queues
                    for e in emails:
                        email_queue.put(e)
                    for h in http:
                        http_queue.put(h)
                    
                    with open("/tmp/count.txt", 'w') as f:
                        print >> f, "Count: %d\nEmails: %d\nHTTP: %s" % (count, len(emails), len(http))
                    
                    
                except Exception, err: 
                    db.close_connection()
                    
                    with open("/tmp/queue-daemon.in", 'w') as f:
                        f.write(traceback.format_exc())
                
                time.sleep(settings.JMS_SETTINGS["resource_manager"]["poll_interval"])
        except Exception, err:
            with open("/tmp/queue-daemon.out", 'w') as f:
                f.write(traceback.format_exc())
                    

                       
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

