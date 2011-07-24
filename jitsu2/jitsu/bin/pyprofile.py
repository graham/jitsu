#! /usr/bin/env python2.5

import os
import re

def find_file(root='.', filetypes=[], max_depth=-1, _depth=0, dirs=0, hidden=1):
    files = []
    if os.path.isfile(root):
        return [root]
    for i in os.listdir(root):
        if i.startswith('.') and not hidden:
            pass
        elif os.path.isdir(root + os.path.sep + i):
            if max_depth == -1 or (_depth <= max_depth):
                tmp = root + os.path.sep + i
                files = files + find_file(tmp, filetypes, _depth=_depth+1, max_depth=max_depth, hidden=hidden)
            else:
                return []
            if dirs:
                files.append(root + os.path.sep + i + os.path.sep)
        else:
            if filetypes != []:
                for filetype in filetypes:
                    if re.match(filetype, i):
                        files.append(root + os.path.sep + i)
            else:
                files.append(root + os.path.sep + i)
    return files

def get_info(l):
    line = 0
    char = 0
    for i in l:
        f = open(i).read()
        char += len(f)
        line += f.count('\n')
    
    return "\t%i / %i / %2.2f" % (len(l), line, line/float(len(l)))

if __name__ == '__main__':
    roots = ['jitsu/server/', 'jitsu/orm/', 'jitsu/template/', 'jitsu/apps/', 'jitsu/modules/']

    for i in roots:
        print('Root: %s' % i)
        py = find_file(root=i, filetypes=['(.*)\.py'], hidden=1)
        tm = find_file(root=i, filetypes=['(.*)\.tmpl'], hidden=1)
        mtm = find_file(root=i, filetypes=['(.*)\.mako'], hidden=1)
        js = find_file(root=i, filetypes=['(.*)\.js'], hidden=1)
        css = find_file(root=i, filetypes=['(.*)\.css'], hidden=1)
        sql = find_file(root=i, filetypes=['(.*)\.sql'], hidden=1)

        if len(py):
            print('   Python Files.     \t'     , get_info(py))
        if len(tm):                         
            print('   Cheetah Templates.\t'  , get_info(tm))
        if len(mtm):                        
            print('   Mako Templates.   \t'    , get_info(mtm))
        if len(js):                         
            print('   JavaScript Files. \t'  , get_info(js))
        if len(css):                        
            print('   CSS Files.          \t'    , get_info(css))
        if len(sql):                        
            print('   SQL Files.          \t'    , get_info(sql))

        print()

        
        