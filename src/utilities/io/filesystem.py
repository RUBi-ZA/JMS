import os, shutil, pwd, grp

class File:
    
    @staticmethod
    def print_to_file(filename, data, mode = 'w', permissions = 0775):
        with open(filename, mode) as f:
            f.write(str(data))
        os.chmod(filename, permissions)    
    
    
    @staticmethod
    def read_file(path):
        content = ""
        with open(path, 'r') as file:
            content = file.read()
        return content
    
    
    @staticmethod
    def copy_file(source, destination, permissions = 0775):
        if (os.path.isfile(source)):
            shutil.copy(source, destination)
            os.chmod(destination, permissions)
    
    
    @staticmethod
    def set_owner(path, user, group, recursive=False, exclude=[]):  
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam(group).gr_gid
        
        if recursive:
            for root, dirs, files in os.walk(path):  
                for momo in dirs:
                    full_path = os.path.join(root, momo)
                    if full_path not in exclude:
                        os.chown(full_path, uid, gid)
                for momo in files:
                    full_path = os.path.join(root, momo)
                    if full_path not in exclude:
                        os.chown(full_path, uid, gid)
        else:
            os.chown(path, uid, gid)


 
class Directory:

    @staticmethod
    def create_directory(path, permissions = 0775):
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(path, permissions)
    
    @staticmethod
    def copy_directory(source, destination, permissions = 0775):
        Directory.create_directory(destination, permissions)
        
        src_files = os.listdir(source)
        for file_name in src_files:
            full_file_name = os.path.join(source, file_name)
            full_dest_name = os.path.join(destination, file_name)
            
            if os.path.isfile(full_file_name):
                File.copy_file(full_file_name, full_dest_name, permissions)
            else:
                Directory.copy_directory(full_file_name, full_dest_name)
    
