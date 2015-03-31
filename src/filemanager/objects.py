import os, shutil, platform, json
from django.conf import settings

class DirectoryObject:
    
    def __init__(self, name, fullpath, type, root="/"):
        self.name = name
        self.fullpath = fullpath
        self.type = type
        self.root = root
    
    
    def create(self):
        directory = os.path.join(self.root, self.fullpath.lstrip("/"))
        name = os.path.join(directory, self.name)
        
        if os.path.exists(directory):
            if self.type == "directory":
                os.makedirs(name)
            else:
                open(name, 'a').close()
        else:
            raise Exception("Parent directory does not exist")
    
    
    def rename(self):
        abs_path = os.path.join(self.root, self.fullpath.lstrip("/"))
        newpath = os.path.join(os.path.dirname(abs_path), self.name)
        os.rename(abs_path, newpath)
    
    
    def copy(self, dst):
        abs_src = os.path.join(self.root, self.fullpath.lstrip("/"))
        abs_dst = os.path.join(self.root, dst.lstrip("/"))
        
        if os.path.isdir(abs_src):
            shutil.copytree(abs_src, os.path.join(abs_dst, self.name))
        else:
            shutil.copy(abs_src, abs_dst)
    
    
    def move(self, dst_dir):
        abs_src = os.path.join(self.root, self.fullpath.lstrip("/"))
        abs_dst = os.path.join(self.root, dst_dir.lstrip("/"))
        shutil.move(abs_src, os.path.join(abs_dst, self.name))
    
    
    def delete(self):
        abs_path = os.path.join(self.root, self.fullpath.lstrip("/"))
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        else:
            os.remove(abs_path)



class Directory:

    def __init__(self, path, root="/"):
        self.root = root
        self.cwd = self.GetDirectoryDetails(path)
        self.dir_contents = self.ListDir(path)    
    
    
    def GetDirectoryDetails(self, path):
        cwd = []
        
        dirs = path.split(os.path.sep)
        
        #On non-Windows machines, the first item in the directory array will be a /
        if platform.system != "Windows":
            dirs[0] = os.path.sep
        
        index = 0    
        for dir in dirs:
            if len(dir) > 0:
                path = dir
                                
                if index >= 1:                    
                    path = os.path.join(cwd[index - 1].fullpath, dir)
                    dir = dir + os.path.sep                
                
                obj = DirectoryObject(dir, path, "directory")
                cwd.append(obj)
            else:
                break
            
            index += 1
        return cwd
    
    
    def ListDir(self, path):
        dir_contents = []
        
        abs_path = os.path.join(self.root, path.lstrip("/"))   
        files = os.listdir(abs_path)
        
        for f in files:
            obj = None
            if os.path.isdir(os.path.join(abs_path, f)):
                obj = DirectoryObject(f, os.path.join(path, f), "directory")
            else:
                obj = DirectoryObject(f, os.path.join(path, f), "file")
                
            dir_contents.append(obj)
            
        return dir_contents
    
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    

class Settings:
    
    def __init__(self, home_directory, theme, font_size):
        self.home_directory = home_directory
        self.theme = theme
        self.font_size = font_size
        
    
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
