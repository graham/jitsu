def get_all_modules():
    import jitsu
    import jitsu.config
    import jitsu.config.server

    core_path = jitsu.__path__[0]
    core_modules = []
    
    return jitsu.config.server.modules

class JitsuModule(object):
    def __init__(self):
        self.ready = False
        self.paths = {}
        
    def load_module(self, paths):
        import select
        import sys
    
        for i in paths:
            print('Loading module %s' % i)
        
            module = __import__(i)
        
            for i in i.split('.')[1:]:
                module = getattr(module, i)
                
            self.paths[i] = module
        
        self.ready = True

        
        