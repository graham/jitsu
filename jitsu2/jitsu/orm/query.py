import copy

class And(object):
    def __init__(self, l):
        self.l = l
    
    def add(self, o):
        self.l.append(o)
    
    def __iter__(self):
        for i in self.l:
            yield i
            
    def __ne__(self):
        return self.Not()
            
    def Not(self):
        n = Or([])

        for i in self.l:
            n.add(i.Not())
        
        return n            

    def render(self, escape_char):
        text_list = []
        args_list = []
        for i in self.l:
            text, args = i.render(escape_char)
            text_list.append(text)
            args_list += args
        return ' and '.join(text_list), args_list

class Or(object):
    def __init__(self, l):
        self.l = l
    
    def add(self, o):
        self.l.append(o)
    
    def Not(self):
        n = And([])

        for i in self.l:
            n.add(i.Not())
        
        return n

    def __iter__(self):
        for i in self.l:
            yield i
    
    def render(self, escape_char):
        text_list = []
        args_list = []
        for i in self.l:
            text, args = i.render(escape_char)
            text_list.append(text)
            args_list += args
        return ' or '.join(text_list), args_list
        
class Condition(object):
    symbol = '???'
    use_value = True
    inverse = None
        
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __iter__(self):
        yield self
            
    def render(self, escape_char):
        if self.use_value:
            return "%s %s %s" % (self.key, self.symbol, escape_char), [self.value]
        else:
            return "%s %s" % (self.key, self.symbol), []
    
    def Not(self):
        return self.conditions[self.inverse](self.key, self.value)
        
class Equals(Condition):
    symbol = '='
    inverse = 'not'

class NotEquals(Condition):
    symbol = '!='
    inverse = 'equals'
    
class GreaterThan(Condition): 
    symbol = '>'
    inverse = 'lte'
    
class GreaterThanOrEqual(Condition): 
    symbol = '>='
    inverse = 'lt'
    
class LessThan(Condition): 
    symbol = '<'
    inverse = 'gte'
    
class LessThanOrEqual(Condition): 
    symbol = '<='
    inverse = 'gt'

class InCollection(Condition): 
    symbol = 'in'
    inverse = 'not_in'
    
class NotInCollection(Condition):
    symbol = 'not in'
    inverse = 'in'
    
class LikeString(Condition): 
    symbol = 'like'
    inverse = 'not_like'
    
class NotLikeString(Condition): 
    symbol = 'not like'
    inverse = 'like'
    
class ContainsString(Condition): 
    symbol = 'contains'
    inverse = 'not_contains'
    
class NotContainsString(Condition):
    symbol = 'does not contain'
    inverse = 'contains'
    
class IsNull(Condition): 
    symbol = 'is null'
    use_value = False
    inverse = 'not_null'

class NotNull(Condition):
    symbol = 'is not null'
    use_value = False
    inverse = 'is_null'


Condition.conditions = {
        'not':NotEquals,
        'equals':Equals,
        'is':Equals,
        'gt':GreaterThan,
        'gte':GreaterThanOrEqual,
        'lt':LessThan,
        'lte':LessThanOrEqual,
        'in':InCollection,
        'not_in':NotInCollection,
        'not_like':NotLikeString,
        'like':LikeString,
        'contains':ContainsString,
        'not_contains':NotContainsString,
        'is_null':IsNull,
        'not_null':NotNull
    }

class GenericQuery(object):
    base_condition = Condition
    def __init__(self, table=None):
        self.table = table
        self.table_name = self.table.table_name
        self.fields = self.table.fields
        self.query = None
        self._order = None
        self._limit = None
        self._offset = None
        self._cached_result = None
        self._locked = False
    
    def lock(self):
        self._locked = True

    def __repr__(self):
        return str(self.run())

    def run(self):
        if not self._cached_result:
            self._cached_result = self.table._result_from_query(self)
        return self._cached_result
        
    def __iter__(self):
        r = self.run()
        for i in r:
            yield i
            
        
    def first(self):
        r = self.run()
        return r.first()
    def last(self):
        r = self.run()
        return r.last()

    def __len__(self):
        return len(self.run())
    def __getslice__(self, *args, **kwargs):
        return self.run().__getslice__(*args, **kwargs)
    def __getitem__(self, *args, **kwargs):
        return self.run().__getitem__(*args, **kwargs)
        
    def _do_copy(self):
        cr = self._cached_result
        self._cached_result = None
        r = copy.copy(self)
        self._cached_result = cr
        return r
    
    def all_columns(self, *args, **kwargs):
        self.fields = self.table.fields
        
    def only_columns(self, *args, **kwargs):
        new = self._do_copy()
        new.fields = []
        for i in args:
            if i in self.table.fields:
                new.fields.append(i)
                
        if self.table.primary_key not in new.fields:
            new.fields.append(self.table.primary_key)

        return new
    
    def exclude_columns(self, *args, **kwargs):
        new = self._do_copy()
        
        new.fields = []
        for i in self.table.fields:
            if i in args:
                pass
            else:
                new.fields.append(i)

        if self.table.primary_key not in new.fields:
            new.fields.append(self.table.primary_key)

        return new
        
    def Not(self):
        new = self._do_copy()
        if self._locked:
            pass
        else:
            new.query = self.query.Not()
        return new
        
    def limit(self, count):
        x = self._do_copy()
        x._limit = count
        return x
    
    def offset(self, count):
        x = self._do_copy()
        x._offset = count
        return x

    def order(self, by):
        x = self._do_copy()
        x._order = by
        return x
        
    def filter(self, **kwargs):
        return self.And(**kwargs)
        
    def filterNot(self, **kwargs):
        pass
    
    def filterOr(self, **kwargs):
        return self.Or(**kwargs)
        
    def exclude(self, **kwargs):
        return self.And(**kwargs).Not()
    
    def Or(self, **kwargs):
        if len(kwargs) == 1:
            for i in kwargs:
                if '__' in i:
                    key, condition = i.rsplit("__", 1)
                    if condition in self.base_condition.conditions:
                        a = self.base_condition.conditions[condition](key, kwargs[i])
                    else:
                        a = self.base_condition(i, kwargs[i])
                else:
                    a = Equals(i, kwargs[i])
        else:
            a = Or([])
            for i in kwargs:
                if '__' in i:
                    key, condition = i.rsplit("__", 1)
                    if condition in self.base_condition.conditions:
                        a.add(self.base_condition.conditions[condition](key, kwargs[i]))
                    else:
                        a.add(self.base_condition(i, kwargs[i]))
                else:
                    a.add(Equals(i, kwargs[i]))
            
        x = self._do_copy()

        if self.query:
            x.query = And([self.query, a])
        else:
            x.query = a

        return x        
    
    def And(self, **kwargs):
        if len(kwargs) == 1:
            for i in kwargs:
                if '__' in i:
                    key, condition = i.rsplit("__", 1)
                    if condition in self.base_condition.conditions:
                        a = self.base_condition.conditions[condition](key, kwargs[i])
                    else:
                        a = self.base_condition(i, kwargs[i])
                else:
                    a = Equals(i, kwargs[i])
        else:
            a = And([])
            for i in kwargs:
                if '__' in i:
                    key, condition = i.rsplit("__", 1)
                    if condition in self.base_condition.conditions:
                        a.add(self.base_condition.conditions[condition](key, kwargs[i]))
                    else:
                        a.add(self.base_condition(i, kwargs[i]))
                else:
                    a.add(Equals(i, kwargs[i]))

        x = self._do_copy()

        if self.query:
            x.query = And([self.query, a])
        else:
            x.query = a

        return x
    
    def count(self):
        r = self._do_copy()
        r.fields = ['count(*)']
        x = r.run().first()
        return x.values['count(*)']