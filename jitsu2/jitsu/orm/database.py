from contextlib import contextmanager

class Database(object):
    def __init__(self, connector):
        self.connector = connector
        self.log_file = open("database_log.txt", 'a')
        
    def initialize(self):
        pass
        
    def log(self, row, description):
        self.log_file.write( "%s\t%r\t%s\n" % (row.table.table_name, row.primary_key(), description) )
        
    def execute(self, query, vars):
        cursor = self.connector.create_cursor()
        cursor.execute(query, vars)
        return cursor.fetchall()
    

    @contextmanager
    def transaction(name):
        print("<%s>" % name)
        yield
        print("</%s>" % name)