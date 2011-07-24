from jitsu.orm.tests.mytest import MyTest
from jitsu.orm.easy_connect import temp_sqlite

class Test_SQLite_Connect(MyTest):
    def setUp(self):
        self.db = temp_sqlite()
            
    def tearDown(self):
        self.db = None

    def test_create_database(self):
        assert self.db != None
        assert self.db.tables == {}
    
    def test_create_table(self):
        self.db.execute('create table foo ( id integer primary key, name varchar(128) );', [])
        self.db.initialize()
        assert 'foo' in self.db.tables
    
    def test_create_row(self):
        self.db.execute('create table foo ( id integer primary key, name varchar(128) );', [])
        self.db.initialize()
        assert 'foo' in self.db.tables

        foo = self.db.get_table('foo')
        assert foo != None
        
        row = foo.create(name='graham')
        row.save()
        
        assert row.primary_key() != None
        
        fetched_row = foo.filter_one(name='graham')
        getted_row = foo.get(row.id)
        
        assert fetched_row.id == getted_row.id
        assert fetched_row.id == row.id
    
    def test_delete_row(self):
        