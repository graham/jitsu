from jitsu.orm.query import *
from jitsu.orm.record import *

# class SQLContains(ContainsString):
#     symbol = 'like'
#     
#     def __repr__(self):
#         return ("%s %s '%%%%%s%%%%'" % (self.key, self.symbol, self.value))
#         
#     def render(self):
#         return ("%s %s ?")
#         
# class SQLStartsWith(ContainsString):
#     symbol = 'like'
#     def __repr__(self):
#         return ("%s %s '%s%%%%'" % (self.key, self.symbol, self.value))
#         
#     def render(self):
#         return ("%s %s ?")
# 
# class SQLEndsWith(ContainsString):
#     symbol = 'like'
#     def __repr__(self):
#         return ("%s %s '%s%%%%'" % (self.key, self.symbol, self.value))
#         
#     def render(self):
#         return ("%s %s ?")
# 
#         
class SQLCondition(Condition):
    pass
# 
# SQLCondition.conditions['contains'] = SQLContains
# SQLCondition.conditions['startswith'] = SQLStartsWith
# SQLCondition.conditions['endswith'] = SQLEndsWith

class SQLQuery(GenericQuery):
    base_condition = SQLCondition
    
    def __init__(self, *args, **kwargs):
        GenericQuery.__init__(self, *args, **kwargs)
        self.eager_fields = []
        
    def build_query(self):
        q = "SELECT %s FROM %s" % (', '.join(self.fields), self.table.table_name)
        cond, vars = self.query.render('?')
        new_vars = []
        
        for i in vars:
            if issubclass(i.__class__, GenericRecord):
                new_vars.append(i.primary_key())
            else:
                new_vars.append(i)
        vars = new_vars
        if cond:
            q += ' WHERE ' + cond
        
        if self._limit:
            q += ' LIMIT ? '
            vars.append(self._limit)
        
        if self._offset:
            q += ' OFFSET ? '
            vars.append(self._offset)
            
        if self._order:
            q += ' ORDER BY ? '
            vars.append(self._order)
        
        q += ';'
        return q, vars

    def eager(self, *args):
        r = self._do_copy()
        for i in args:
            if i not in r.eager_fields:
                r.eager_fields.append(i)
        return r
        