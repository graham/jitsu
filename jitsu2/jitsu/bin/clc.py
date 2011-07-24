#! /usr/bin/env python2.5
import os
import re
import sys

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
                fffff = root + os.path.sep + i + os.path.sep
                files.append(fffff.replace('//', '/'))
        else:
            if filetypes != []:
                for filetype in filetypes:
                    if re.match(filetype, i):
                        fffff = root + os.path.sep + i
                        files.append(fffff.replace('//', '/'))
            else:
                files.append(root + os.path.sep + i)
    return files
    
if __name__ == '__main__':
    p = os.path.abspath('.')
    print(p)
    x = find_file(root=p, filetypes=['(.*).pyc$', '(.*).pyo$', '(.*).log$', '(.*)~$', '(.*)\.DS_Store$', '(.*)\._(.*)'], dirs=0)

    for i in x:
        print("Deleting %s" % i)
        try:
            os.remove(i)
        except:
            pass



