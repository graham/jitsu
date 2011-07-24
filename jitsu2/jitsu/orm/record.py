class GenericRecord(object):
    def __init__(self, connector, database, fields, rvalues, result):
        self.connector = connector
        self.database = database
        self.fields = fields
        self.values = rvalues

        self.foreign_values = {}
        self.constraints = {}
        self.changed = []
        
        self.result = result
        
    def primary_key(self):
        return None

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, ', '.join(["%s=%r" % (i, self.values[i]) for i in self.values]))
    def safe_repr(self):
        return self.__repr__().replace('<', '[').replace('>', ']')
        
    def save(self):
        pass
    
    def load(self):
        pass
        
    def delete(self):
        pass
    
    def _log(self):
        import time
        return '%s changed at %s' % (self.changed, time.asctime())
    
    def _commit_log(self, message):
        self.database.log(self, message)
        
    def update_record(self, fields, rvalues):
        pass
    
    def create_record(self, fields, rvalues):
        pass
    
    def validate_values(self):
        pass
        
    def as_json(self):
        import json
        return json.dumps(self.values)
        
    def save_and_log(self):
        log_message = self._log()
        self.save()
        self._commit_log(log_message)

class GenericTable(object):
    def __init__(self, connector, table_name):
        self.connector = connector
        self.table_name = table_name

        self.search_fields = []
        self.list_fields = []
        self.filter_fields = []
        self.field_groups = []

        self.actions = {}
        self.validators = {}

    def filter(self, **kwargs):
        pass
    
    def delete(self, **kwargs):
        pass