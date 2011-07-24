class GenericConnector(object):
    def __init__(self, mode=1):
        self.mode = mode
        
    def translate(self, q):
        return q
    
    def translate_data(self, rvars):
        return rvars
        
    def create_connection(self):
        pass
        
class GenericCursor(object):
    # Most people wont need this.
    pass