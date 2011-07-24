def connect_sqlite(path):
    from jitsu.orm.adapter.sqlite.connect import SQLiteConnector
    from jitsu.orm.adapter.sqlite.record import SQLiteDatabase
    x = SQLiteConnector(path)
    database = SQLiteDatabase(x)
    database.initialize()
    return database

def temp_sqlite():
    import tempfile
    tempfile.tempdir = '/tmp/'
    filename = tempfile.mktemp(prefix='orm_db_test_')
    return connect_sqlite(filename)

