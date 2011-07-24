# Jitsu 8.9
import sys
sys.path.append('libs')

def verbose_level():
    return 10
    
def jitsu_path():
    import jitsu
    return jitsu.__path__[0]
    
def blurg():
    return ' word'
    
def safe_split(string, delimiters, openers, closers):
    tokens = []
    depth = 0
    buf = ''
    
    if string:
        for i in string:
            if i in openers:
                depth += 1
            elif i in closers:
                depth -= 1
        
            if depth:
                buf += i
            else:
                if i in delimiters:
                    tokens.append(buf)
                    buf = ''
                else:
                    buf += i
                
        if buf:
            tokens.append(buf)
        
        return tokens    
    else:
        return []
