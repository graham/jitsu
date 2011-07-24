from jitsu.orm.record import GenericRecord, GenericTable
from jitsu.orm.adapter.sql.query import SQLQuery
from jitsu.orm.adapter.sql.result import SQLResult

class SQLRecord(GenericRecord):
    def __init__(self, connector, database, fields, rvalues, result, table):
        GenericRecord.__init__(self, connector, database, fields, rvalues, result)
        self.is_new = False
        if rvalues == {}:
            self.is_new = True
        self.table = table
        
    def primary_key(self):
        return self.values[self.table.primary_key]
        
    def __getattribute__(self, key):
        d = object.__getattribute__(self, '__dict__')
        try:
            if key in d['table'].foreign_keys:
                if key in d['foreign_values']:
                    pass
                else:
                    d['foreign_values'][key] = d['database'].get_table(d['table'].foreign_keys[key]).get(d['values'][key])
                    if self.result:
                        self.result.foreign_data_fetched(key)
                return d['foreign_values'][key]                
            elif key in d['fields']:
                return d['values'][key]
            else:
                return object.__getattribute__(self, key)    
        except:
            import traceback
            traceback.print_exc()
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        d = object.__getattribute__(self, '__dict__')
        try:
            if key in d['foreign_values']:
                if d['foreign_values'][key] == value:
                    pass
                else:
                    d['foreign_values'][key] = value
                    d['changed'].append(key)
            elif key in d['fields']:
                if key in d['values']:
                    old_value = d['values'][key]

                    if old_value == value:
                        pass
                    else:
                        d['values'][key] = value
                        d['changed'].append(key)
                else:
                    d['values'][key] = value
                    d['changed'].append(key)
            else:
                return object.__setattr__(self, key, value)
        except:
            return object.__setattr__(self, key, value)

    def save_and_log(self):
        log_message = self._log()
        self.save()
        self._commit_log(log_message)
        
    def save(self):
        if self.is_new:
            insert = []
            rvalues = []
            for i in self.fields:
                if i != self.table.primary_key:
                    insert.append(i)
                    val = self.values[i]
                    if issubclass(val.__class__, GenericRecord):
                        val = val.primary_key()
                    rvalues.append(val)
                        
            self.validate_values()
            self.create_record( insert, rvalues )
            self.is_new = False
            
        else:
            insert = []
            rvalues = []
            
            for i in self.changed:
                insert.append(i)
                val = self.values[i]
                rvalues.append(val)
            
            if insert and rvalues:
                self.validate_values()
                self.update_record( insert, rvalues )
                self.changed = []

        return self

class SQLTable(GenericTable):
    query_class = SQLQuery
    record_class = SQLRecord
    result_class = SQLResult
    escape_char = '?'
    
    def __init__(self, connector, database, table_name):
        self.connector = connector
        self.database = database
        self.table_name = table_name
        self.fields = {}
        self.field_types = {}
        self.foreign_keys = {}
        self.primary_key = None
        
    def inspect(self):
        pass
    
    def filter(self, **kwargs):
        return self.query_class(self).And(**kwargs)
        
    def filter_one(self, **kwargs):
        q = self.query_class(self).And(**kwargs).limit(1)
        return q.first()
        
    def create(self, **kwargs):
        r = self.record_class(self.connector, self.database, self.fields, {}, None, self)
        for i in kwargs:
            setattr(r, i, kwargs[i])
        return r

    def get(self, key, revision=None):
        cursor = self.connector.create_cursor()
        cursor.execute(q='SELECT * FROM %s WHERE %s=%s' % (self.table_name, self.primary_key, self.escape_char), rvars=[key])
        return self.record_class(self.connector, self.database, self.fields, cursor.fetchone(), None, self)

    def get_or_create(self, **kwargs):
        result = self.filter_one(**kwargs)
        if result:
            return result, False
        else:
            return self.create(**kwargs), True
    
    def get_or_insert(self, **kwargs):
        row, created = self.get_or_create(**kwargs)
        if created:
            row.save()
        return row
        
    def _result_from_query(self, query_object):
        cursor = self.connector.create_cursor()
        b, args = query_object.build_query()
        cursor.execute(b, args)
        result = self.result_class(query_object, self, cursor)
        return result
        
    def _record_from_dict(self, data, result):
        r = self.record_class(self.connector, self.database, self.fields, data, result, self)
        return r
    
