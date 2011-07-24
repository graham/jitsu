def dict_one(cursor, x):
    colnames = [t[0] for t in cursor.cursor.description]
    if x:
        if type(x) == dict:
            return x
        else:
            return dict(zip(colnames, x))
    else:
        return {}
        
def dict_all(cursor):
    if cursor.rowcount:
        res = cursor.fetchall()
    else:
        res = {}
        
    if res:
        if type(res[0]) == dict:
            return res
        else:
            r = []
            for i in res:
                r.append(dict_one(cursor, i))
            return r
    else:
        return {}
        

def safe_split(string, delimiters, openers, closers):
    tokens = []
    depth = 0
    buf = ''
    
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