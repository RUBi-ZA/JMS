import threading

class TimeExpiredDict:
    
    def __init__(self, timeout):
        self.lock = threading.Lock()
        self.timeout = timeout
        self.container = {}
        

    def add(self, key, value):    
        with self.lock:
            self.container[key] = value
            threading.Timer(self.timeout, self.expire, args=(key,)).start()
            return True
    
    
    def get(self, key):
        with self.lock:
            return self.container.get(key, None)
            

    def expire(self, key):
        with self.lock:
            self.container.pop(key, None)
            

    def __len__(self):
        with self.lock:
            return len(self.container)


    def __str__(self):
        with self.lock:
            return 'Container: %s' % str(self.container.keys())


    def __contains__(self, val):
        with self.lock:
            return val in self.container
            
            
