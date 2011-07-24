from jitsu.orm.result import Result

EAGER_COUNT = 2

class SQLResult(Result):
    def __init__(self, query, table, cursor):
        Result.__init__(self, query, table, cursor)
        self.foreign_fetches = {}

    def foreign_data_fetched(self, field):
        if field in self.foreign_fetches:
            self.foreign_fetches[field] += 1
        else:
            self.foreign_fetches[field] = 1
        
        if self.foreign_fetches[field] >= EAGER_COUNT:
            row = self.first()
            if row: # this has to be true but just in case
                target_table = row.table.foreign_keys[field]
                tt = row.table.database.get_table(target_table)
            else:
                pass
