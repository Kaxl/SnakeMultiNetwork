class Timer():
    
    def __init__(self,timeout,init_time,periodic=False):
        self.timeout=timeout
        self.init_time=init_time
        self.active=True
        self.periodic=periodic

    def change(self,timeout):
        self.timeout=timeout

    def activate(self,current_time):
        self.init_time=current_time
        self.active=True
    
    def expired(self,current_time):
        if self.active:
            if current_time - self.init_time > self.timeout:
                if self.periodic:
                    self.activate(current_time)
                return True
        return False

