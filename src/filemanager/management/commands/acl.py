from django.core.management.base import BaseCommand
from django.conf import settings

import os, json, mimetypes, platform, shutil, traceback, sys, getpass

from filemanager.objects import *
from filemanager.models import *

class Command(BaseCommand):
    args = '<operation [param_1 param_2 ...]>'
    help = 'Parameters are specific to the operation being performed'
    
    def handle(self, *args, **options):
        
        op = args[0]
        output = ""
        root = os.path.join(settings.FILEMANAGER_SETTINGS["root_url"], getpass.getuser())
        root = os.path.join(root, "jobs/")
        
        try:
            if op == "GET_DIR":
                root = args[1]
                path = args[2]
                if path.endswith(":"):
                    path += "\\"    
                
                directory = Directory(path, root)
                
                output = directory.to_JSON()
            elif op == "CREATE_TEMP_FILE":                    
                path = args[1]
                output = args[2]
                
                if os.path.exists(output):
                    os.remove(output)
                    
                shutil.copyfile(path, output)
                os.chmod(output, 0755)             
            elif op == "CREATE":            
                dir_obj = DirectoryObject(args[1], args[2], args[3], root)
                dir_obj.create()            
            elif op == "RENAME":
                dir_obj = DirectoryObject(args[1], args[2], args[3], root)
                dir_obj.rename()
            elif op == "MOVE":
                dir_obj = DirectoryObject(args[1], args[2], args[3], root)
                dir_obj.move(args[4])
            elif op == "COPY":
                dir_obj = DirectoryObject(args[1], args[2], args[3], root)
                dir_obj.copy(args[4])
            elif op == "DELETE":
                dir_obj = DirectoryObject(args[1], args[2], args[3], root)
                dir_obj.delete()
            elif op == "OVERWRITE_FILE":                
                path = os.path.join(root, args[1].lstrip("/"))
                tmp_file = args[2]
                shutil.copyfile(tmp_file, path)   
                os.remove(tmp_file)             
            else:
                output = "ERROR:\n\nInvalid operation"
        except Exception, err:
            output = "ERROR:\n\n%s" % str(err)
        
        return output
