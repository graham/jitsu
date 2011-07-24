class GenericDataType(object):
    python_type = str
    
    def __init__(self, raw_type, adds):
        self.null = False
        self.blank = False
        self.size = 0
        
        self.raw_type = raw_type
        self.additional = adds
        
        if 'not null' in self.additional:
            null = False
        
        self.init()
        
    def init(self):
        pass
        
    def load(self, data):
        try:
            data = self.python_type(data)
        except:
            pass
        return data
    
    def save(self, data):
        try:
            data = self.python_type(data)
        except:
            pass
        return data
    
class IntegerType(GenericDataType):
    python_type = int
    
class FloatType(GenericDataType):
    python_type = float

class BooleanType(GenericDataType):
    python_type = bool
    
class VarCharType(GenericDataType):
    python_type = str
    
    def init(self):
        self.size = int(self.raw_type.split('(')[1].rstrip(')'))

class CharType(GenericDataType):
    python_type = str

class TextType(GenericDataType):
    python_type = str
    
class DateTimeType(GenericDataType):
    import datetime
    python_type = datetime.datetime
    
class EpochType(GenericDataType):
    import datetime
    import time
    python_type = int
    
    def load(self, data):
        if type(data) == datetime.datetime:
            return data
        elif type(data) == int:
            return datetime.datetime.from_timestamp(data)
    
    def save(self, data):
        if type(data) == datetime.datetime:
            return time.mktime(data.timetuple())
        elif type(data) == int:
            return data

        