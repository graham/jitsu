def parse_cookies(cookie_data):
    request_cookies = {}
    if cookie_data == '':
        return {}

    for i in cookie_data.split(";"):
        j = i.split("=")
        request_cookies[j[0].strip()] = j[1].strip()
            
    return request_cookies

def parse_environ(data):
    environ = {}
    for i in data:
        environ[i] = data[i]
    return environ

def parse_form_data(request_type, url, raw):
    request_type = request_type.upper().strip()
    form_data = {}
    form_data_raw = ''

    if request_type == 'GET':
        if '?' in url:
            j = url.split("?", 1)
            url = j[0]
            form_data_raw = j[1]
    elif request_type == 'POST':
        form_data_raw = raw
        if '?' in url:
            j = url.split("?", 1)
            url = j[0]
            form_data_raw += '&' + j[1]
    elif request_type == 'DELETE':
        if '?' in url:
            j = url.split("?", 1)
            url = j[0]
            form_data_raw = j[1]
    elif request_type == 'PUT':
        form_data = {'PUT_data':raw}
    else:
        print('Sorry but i dont know how to handle a %s' % request_type)
        
    if form_data_raw:
        for i in form_data_raw.split("&"):
            if '=' not in i:
                pass
            else:
                j = i.split("=", 1)
                value = None
                if len(j) > 1:
                    value = j[1]

                if j[0] in form_data:
                    form_data[j[0]].append(j[1])
                else:
                    form_data[j[0]] = [j[1]]
                
    if form_data:
        for i in form_data:
            n = []
            for j in form_data[i]:
                n.append(clean_input(j))
            form_data[i] = n
                            
    return url, form_data

def clean_input(data):
    orig_data = data
    new_data = ''
    
    prev_loc = 0
    loc = orig_data.find('%')
    while loc != -1:
        new_data += orig_data[prev_loc:loc]
        prev_loc = loc
        number = int('0x'+orig_data[loc+1:loc+3], 0)

        new_data += chr(number)
        
        loc += 3
        prev_loc = loc
        loc = orig_data.find('%', loc)
        
        new_data = new_data.replace('+', ' ')
    new_data += orig_data[prev_loc:]
    
    new_data = new_data.replace('+', ' ')
    new_data = new_data.replace(';', '\\;')

    return new_data
    
    