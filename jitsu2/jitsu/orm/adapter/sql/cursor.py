from jitsu.orm.connect import GenericCursor
import jitsu.orm
import time
import traceback

import sys

class SQLCursor(GenericCursor):
    def __init__(self, connector):
        self.connector = connector
        self.conn = connector.create_connection()
        self.cursor = self.conn.cursor()

    def execute(self, q, rvars=None):
        q = self.connector.translate(q)
        if rvars:
            rvars = [self.connector.translate_data(i) for i in rvars]

        start = time.time()

        try:
            if rvars:
                self.cursor.execute(q, rvars)
            else:
                self.cursor.execute(q)

            end = time.time()
            

            if jitsu.orm.VERBOSE:
                if getattr(self.cursor, 'query', None):
                    print('%.5f' % (end-start), self.cursor.query, rvars)
                else:
                    print('%.5f' % (end-start), q, rvars)

        ## Change in p3k
        # except Exception, e:
        
        except Exception, e:
            self.conn.rollback()
            if jitsu.orm.VERBOSE:
                print('FAILED', q, rvars)
            traceback.print_exc()
            raise e

    def d_fetchall(self, data):
        colnames = [t[0] for t in self.cursor.description]  
        rows = [dict(zip(colnames, tup)) for tup in data]
        return rows

    def fetchall(self):
        if self.cursor.rowcount:
            res = self.cursor.fetchall()
        else:
            res = {}
            
        if res:
            if type(res[0]) == dict:
                return res
            else:
                return self.d_fetchall(res)
        else:
            return {}

    def fetchone(self):
        colnames = [t[0] for t in self.cursor.description]
        x = self.cursor.fetchone()
        if x:
            if type(x) == dict:
                return x
            else:
                return dict(zip(colnames, x))
        else:
            return {}
            
    def commit(self):
        try:
            start = time.time()
            self.conn.commit()
            end = time.time()
        except:
            import traceback
            traceback.print_exc()
            self.conn.rollback()

    
    def rollback(self):
        try:
            start = time.time()
            self.conn.rollback()
            end = time.time()
        except:
            import traceback
            traceback.print_exc()
            self.conn.commit()

