from jitsu.orm.adapter.sql.record import SQLRecord, SQLTable
from jitsu.orm.database import Database
from jitsu.orm.constraints import d as constraint_list
from jitsu.orm.util import *

import re
        
class SQLiteRecord(SQLRecord):
    def create_record(self, fields, rvalues):
        cursor = self.connector.create_cursor()
        q = [self.table.escape_char] * len(rvalues)
        cursor.execute('insert into %s(%s) values(%s);' % (self.table.table_name, ', '.join(fields), ', '.join(q)), rvalues)
        self.values[self.table.primary_key] = cursor.cursor.lastrowid
        cursor.commit()
    
    def update_record(self, fields, rvalues):
        cursor = self.connector.create_cursor()
        q = [self.table.escape_char] * len(rvalues)
        vals = [i+'='+j for i, j in zip(fields, q)]
        cursor.execute('update %s set %s where %s=%s' % (self.table.table_name, ', '.join(vals), self.table.primary_key, self.values[self.table.primary_key]), rvalues)
        cursor.commit()

class SQLiteTable(SQLTable):
    record_class = SQLiteRecord
    def inspect(self):
        ## Find all Columns
        cursor = self.connector.create_cursor()
        cursor.execute("select sql from sqlite_master where tbl_name='%s'" % self.table_name)
        try:
            schema = str(dict_one(cursor, cursor.fetchone())['sql'].strip())
        # Change in py3k
        #except KeyError, ke:
        except KeyError, ke:
            raise Exception("no table named %s" % self.table_name)
            
        start = schema.find('(')
        end = schema.rfind(')')
        schema = schema[start+1:end].strip()

        cols = []
        consts = {}
        r = {}
        buf = None
        
        for i in safe_split(schema, ',', '(', ')'):
            i = i.strip()
            j = i.split()

            ctype = j[1].strip()
            rest = ' '.join(j[2:])
            restl = rest.lower()

            if j[0].startswith('"') and j[0].endswith('"'):
                j[0] = j[0][1:-1]
        
            if j[0] in constraint_list:
                consts[j[0]] = (j[1], restl)
            else:
                cols.append( j[0] )
                r[j[0]] = (j[1], restl)
            
        self.fields = cols
        self.field_types = r
        self.constraints = consts
        
        ## Find primary key
        sql = cursor.execute("select sql from sqlite_master where tbl_name='%s'" % self.table_name, )
        schema = str(dict_one(cursor, cursor.fetchone())['sql'].strip())
        start = schema.find('(')
        end = schema.rfind(')')
        schema = schema[start+1:end].strip()
        
        for i in safe_split(schema, ',', '(', ')'):
            i = i.strip()
            j = i.split()
        
            if j[0].startswith('"') and j[0].endswith('"'):
                j[0] = j[0][1:-1]
        
            rest = ' '.join(j[2:])
            rest = rest.lower()
            if 'primary key' in rest:
                self.primary_key = j[0]
                break
        
        ## Find Foreign Keys
        sql = cursor.execute("select sql from sqlite_master where tbl_name='%s'" % self.table_name)
        schema = str(dict_one(cursor, cursor.fetchone())['sql'].strip())
        start = schema.find('(')
        end = schema.rfind(')')
        schema = schema[start+1:end].strip()
        
        fkeys = {}
        
        for i in safe_split(schema, ',', '(', ')'):
            i = i.strip()
            j = i.split()
        
            if j[0].startswith('"') and j[0].endswith('"'):
                j[0] = j[0][1:-1]
        
            rest = ' '.join(j[2:])
            
            if 'references' in rest.lower():
                m = re.search('references (.*)\((.*)\)', rest, re.I)
                table, col = m.groups()
                table = table.replace('"', '').strip()
                col = col.replace('"', '').strip()
                fkeys[j[0]] = str(table)
        
        self.foreign_keys = fkeys
        
        #### now lets determine our data types
        from jitsu.orm.adapter.sql.datatypes import type_list
        from jitsu.orm.adapter.sql.datatypes import ForeignKeyType
        real_types = {}
        
        for i in self.field_types:
            type = self.field_types[i][0]
            if ('(') in type:
                type = type.split('(', 1)[0]
            
            if type in type_list:
                if 'references' in self.field_types[i][1]:
                    real_types[i] = ForeignKeyType(*self.field_types[i])
                else:
                    real_types[i] = type_list[type](*self.field_types[i])
            else:
                print("MISSING TYPE", type)
        
        self.field_types = real_types
            
        
            

class SQLiteDatabase(Database):
    table_class = SQLiteTable
    def __init__(self, connector):
        Database.__init__(self, connector)
        self.tables = {}
        self.foreign_tables = {}
        
    def __getattribute__(self, key):
        d = object.__getattribute__(self, '__dict__')
        if key in d['tables']:
            return self.get_table(key)
        else:
            return object.__getattribute__(self, key)

    def get_table(self, key):
        if key in self.tables:
            return self.tables[key]
        elif key in self.foreign_tables:
            return self.foreign_tables[key]
        else:
            return None
        
    def initialize(self):
        cursor = self.connector.create_cursor()
        cursor.execute("select tbl_name from sqlite_master where type='table'")
        for i in cursor.fetchall():
            table = self.table_class(self.connector, self, i['tbl_name'])
            table.inspect()
            self.tables[i['tbl_name']] = (table)
            
