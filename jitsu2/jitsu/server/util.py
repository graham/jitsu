import sys
#import io
import StringIO as io
import traceback

def steal_stack_trace():
    safe_stderr = sys.stderr
    s = io.StringIO()
    try:
        sys.stderr = s
        traceback.print_exc()
    finally:
        sys.stderr = safe_stderr
    return s.getvalue()

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
    
class FileWatcher(object):
    def __init__(self):
        self.files = {}
        self.callbacks = {}
        self.default_callback = self.callback
        self.running = 1
        
        self.cur_changed = []

    def callback(self, filename, info):
        pass
    
    def reset(self):
        self.cur_changed = []

    def update(self):
        changed_list = []
        remove = []
        for i in self.files:
            try:
                changed = self.file_info(i)
                if changed: 
                    changed_list.append(i)
                    if i not in self.cur_changed:
                        self.cur_changed.append(i)
            except:
                remove.append(i)

        for i in remove:
            self.files.pop(i)
        return changed_list
        
    def file_info(self, filename):
        try:
            cur = os.lstat(filename)
            last = self.files[filename]
            if cur != last:
                self.callback(filename, cur)
                self.files[filename] = cur
                return 1
        except:
            print('problem with %s.' % filename)
            raise Exception("File Broken")
        return 0
