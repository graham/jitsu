from jitsu.orm.adapter.sql.connect import SQLConnector
from jitsu.orm.adapter.sql.cursor import SQLCursor
from jitsu.orm.adapter.sqlite.record import SQLiteTable
import sqlite3

class SQLiteConnector(SQLConnector):
    def __init__(self, location, **kwargs):
        self.location = location
    
    def create_connection(self):
        conn = sqlite3.connect(self.location)
        return conn
        
    def create_cursor(self):
        return SQLCursor(self)
    
