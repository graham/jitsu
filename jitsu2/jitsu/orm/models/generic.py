
class Base(object):
    def __init__(self, null=False):
        self.null = null
        
    def render(self):
        pass
    
    def render_as_python(self):
        pass

    def render_as_sql(self):
        pass

class CharField(object):
    def __init__(self, max_length=128, *args, **kwargs):
        self.max_length = max_length
    
    def render_as_sql(self):
        pass

def get_model_for_sql(sql_line):
    pass

