class Result(object):
    def __init__(self, query, table, cursor):
        self.query = query
        self.table = table
        self.cursor = cursor
        self.data = []
        
        for index, i in enumerate(cursor.fetchall()):
            o = self.table._record_from_dict(i, self)
            o._query_result_index = index
            self.data.append(o)
        
    def __repr__(self):
        return list.__repr__(self.data)
        
    def __iter__(self):
        return self.data.__iter__()
        
    def __getslice__(self, *args, **kwargs):
        return self.data.__getslice__(*args, **kwargs)
    
    def __contains__(self, *args, **kwargs):
        return self.data.__contains__(*args, **kwargs)
        
    def __getitem__(self, *args, **kwargs):
        return self.data.__getitem__(*args, **kwargs)
    
    def __len__(self, *args, **kwargs):
        return self.data.__len__(*args, **kwargs)
        
    def first(self):
        if self.data:
            return self.data[0]
        else:
            return None
    def last(self):
        if self.data:
            return self.data[-1]
        else:
            return None
            
    def foreign_data_fetched(self, field):
        pass