import jitsu.orm
import jitsu.orm.easy_connect
import jitsu.orm.adapater.sql.sqlite
import jitsu.orm.datatypes
import sys

path = '/Users/graham/django/softtouch/data.db'

if len(sys.argv) > 1:
    path = sys.argv[1]
    
db = jitsu.orm.easy_connect.connect_sqlite(path)

print(''')
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

'''

unknowns = []


tables = db.tables.keys()
tables.sort()

modules = []
table_count = 0


for i in tables:
    module, name = i.split("_", 1)

    if module not in modules:
        modules.append(module)
    table_count += 1
    
    if module == "auth" or module == 'django':
        pass
    else:
        name = module+'_'+name
        print('#', module, name)
        print("class %s(models.Model):" % name.replace("_", " ").title().replace(" ", ""))
    
        table = db.tables[i]
    
        for j in table.fields:
            if j == 'id':
                pass
            else:
                fkey = False
                if j.endswith("_id"):
                    j2 = j.rsplit("_", 1)[0]
                else:
                    j2 = j

                field = table.field_types[j]
                types = jitsu.orm.datatypes
                
                if type(field) == types.GenericDataType:
                    print('   ', j2, '=', )
                    print('models.TextField()')
                elif type(field) == types.VarCharType:
                    print('   ', j2, '=', )
                    print('models.CharField(max_length=%s)' % field.size)
                elif type(field) == types.TextType:
                    print('   ', j2, '=', )
                    print('models.TextField()')
                elif type(field) == types.IntegerType:
                    print('   ', j2, '=', )
                    print('models.IntegerField()')
                elif type(field) == types.FloatType:
                    print('   ', j2, '=', )
                    print('models.FloatField()')
                elif type(field) == types.BooleanType:
                    print('   ', j2, '=', )
                    print('models.BooleanField()')
                elif type(field) == types.EpochType:
                    print('   ', j2, '=', )
                    print('models.TimeField()')
                elif type(field) == jitsu.orm.adapter.sql.datatypes.ForeignKeyType:
                    print('   ', j2, '=', )
                    tname = field.foreign_table
                    n = tname.replace("_", " ").title().replace(" ", "")
                    print('models.ForeignKey("%s", db_column="%s")' % (n, j2))
                else:
                    print('UNKNOWN')
                    unknowns.append(type(field))

        print
        
        print('    class Meta:')
        print('        db_table = "%s"' % i)
        print

        print('class %sAdmin(admin.ModelAdmin):' % name.replace("_", " ").title().replace(" ", ""))
        print('    #list_display = ()')
        print('    #list_filter = ()')
        print('    pass')
        print()
        print('admin.site.register(%s, %sAdmin)' % (name.replace("_", " ").title().replace(" ", ""), name.replace("_", " ").title().replace(" ", "")))
        
        print


print('#UNKNOWNS')
for i in unknowns:
    print('    ', '#', i)
    
print('#info')
print('# modules -> ', ', '.join(modules))
print('# count: %i' % table_count)