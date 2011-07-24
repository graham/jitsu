import os
import sys
import time
import gzip
#import io
import StringIO as io
import socket
import select
import cgi
import types


import http
import http.server
requestHandler = http.server.BaseHTTPRequestHandler

normal =         "\033[0m"
red =            "\033[31m"

def compressBuf(buf):
    zbuf = io.StringIO()
    zfile = gzip.GzipFile(mode = 'wb',  fileobj = zbuf, compresslevel = 9)
    zfile.write(buf)
    zfile.close()
    return zbuf.getvalue()

class RequestHandler(requestHandler):
    def is_secure(self):
        return False
        
    def pre_response(self):
        import jitsu
        import jitsu.base
        import jitsu.server.header_parser
        import jitsu.server.runafter
        
        if 'content-length' in self.headers:
            data = {}
            query = {}
            
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            bytes = int(self.headers["content-length"])
            fdata = self.rfile.read(bytes).decode()

            if ctype == 'multipart/form-data':
                if 'boundary' in pdict:
                    for i in fdata.split('--' + pdict['boundary']):
                        if i.strip() == '':
                            pass
                        elif i.strip() == '--':
                            pass
                        else:
                            headers, content = i.split('\r\n\r\n')
                            headers = headers.strip()
                            headers = headers[len('Content-Disposition: form-data; '):]
                            additional = ''
                            if '\r\n' in headers:
                                headers, additional = headers.split('\r\n')
                            
                            more = ''
                            if ';' in headers:
                                name, more = headers.split(';', 1)
                            else:
                                name = headers.strip()
                            
                            name = name.split('=')[1][1:-1]
                            
                            if not more and not additional:
                                if name in query:
                                    query[name].append([content[:-2]])
                                else:
                                    query[name] = [content[:-2]]
                            else:
                                more_d = {}
                                for k in more.split(';'):
                                    if k.strip() == '':
                                        continue
                                    key, value = k.split('=')
                                    value = value[1:-1]
                                    more_d[key.lower().strip()] = value
                                for k in additional.split('\r\n'):
                                    if k.strip() == '':
                                        continue
                                    key, value = k.split(': ')
                                    more_d[key.lower().strip()] = value
                                    
                                if content == '\r\n':
                                    if name in query:
                                        query[name].append(None)
                                    else:
                                        query[name] = [None]
                                else:
                                    if name in query:
                                        query[name].append([content[:-2], more_d])
                                    else:
                                        query[name] = [ [content[:-2], more_d] ]
            else:
                query = cgi.parse_qs(fdata)
                
            for i in query:
                data[i] = query[i]
        else:
            data = {}

        self.client_address = self.client_address[0]
        cookie_data = ''
        if 'cookie' in self.headers:
            cookie_data = self.headers['cookie']
        self.cookies = jitsu.server.header_parser.parse_cookies(cookie_data)
        self.environ = jitsu.server.header_parser.parse_environ(self.headers)

        if 'referer' in self.environ:
            self.hostname = self.environ['referer']
        else:
            self.hostname = ''

        self.url, self.get_form_data = jitsu.server.header_parser.parse_form_data(self.request_type, self.path, '')
        self.post_form_data = data
        
        self.form_data = self.get_form_data.copy()
        self.form_data.update(data)

    def do_GET(self):
        self.request_type = 'GET'
        self.pre_response()
        self.do_response()

    def do_POST(self):
        self.request_type = 'POST'
        self.pre_response()
        self.do_response()
        
    def do_PROPFIND(self):
        self.request_type = 'PROPFIND'
        self.pre_response()
        self.do_response()

    def do_DELETE(self):
        self.request_type = 'DELETE'
        self.pre_response()
        self.do_response()

    def do_PUT(self):
        self.request_type = 'PUT'
        self.pre_response()
        self.do_response()
        
    def handle_response_error(self):
        import jitsu.server.util
        self.write('HTTP/1.1 500 OK\r\n')
        tmp = jitsu.server.util.steal_stack_trace()
        print(tmp)
        self.write('Content-Length: %i\r\n\r\n' % len(tmp))

        self.write(tmp)
        self.wfile.flush()

    def do_response(self):
        start = time.time()
        gzip_response = False
        headers_flushed = False
        buf = []
        
        import jitsu.base
        import jitsu.base.response
        
        try:
            r = jitsu.base.response.Response(url=self.url, raw_url=self.path,
                     form_data=self.form_data, 
                     cookie_data=self.cookies, 
                     environ=self.environ, 
                     ip=self.client_address, 
                     secure=self.is_secure(),
                     request_hostname='localhost',
                     request_type=self.request_type,
                     get_form_data=self.get_form_data,
                     post_form_data=self.post_form_data,
                     server=self.server)

            self.response_object = r
            
            section = r.render()
            
            r.render_headers()
            self.do_write_headers()
            
            continue_after = False
            
            try:
                if types.GeneratorType == type(section):
                    for i in section:
                        if type(i) == jitsu.server.runafter.RunAfter:
                            continue_after = i
                            break;
                        else:
                            self.write(str(i))
                else:
                    self.write(str(i))
                
                self.wfile.flush()
                self.wfile.close()
                r.finish()
            except socket.error:
                print('ERROR: Client Disconnected before recving all information.')
            finally:
                if continue_after:
                    self.server.parent_job_queue.send(continue_after)

        except:
            import traceback
            traceback.print_exc()
            self.handle_response_error()
            return
            

    def do_write_headers(self):
        self.write('HTTP/1.1 %i %s\r\n' % (self.response_object.return_code))
    
        # if self.response_object.headers_dict['Content-Type'] in ('text/html', 'text/plain', 'text/js', 'text/css'):
        #     if 'accept-encoding' in self.environ:
        #         if 'gzip' in self.environ['accept-encoding']:
        #             gzip_response = True
        #             self.response_object.headers_dict['Vary'] = 'Accept-Encoding'
        #             self.response_object.headers_dict['Content-Encoding'] = 'gzip'
        #             #self.response_object.payload = compressBuf(self.response_object.payload)
        #             #self.response_object.headers_dict['Content-Length'] = len(self.response_object.payload)

        for i in self.response_object.headers_dict:
            self.write('%s: %s\r\n' % (i.capitalize(), self.response_object.headers_dict[i]))

        for i in self.response_object.outbound_cookie_dict:
            value = self.response_object.outbound_cookie_dict[i][0]
            add = self.response_object.outbound_cookie_dict[i][1]
            add = ['%s=%s;' % (j, add[j]) for j in add]
            if jitsu.core.config.ALLOW_SUBDOMAIN_ACCESS and self.response_object.full_domain_name and self.response_object.full_domain_name != 'localhost':
                self.write('Set-Cookie: %s=%s;%s; domain=.%s\r\n' % (i, self.response_object.outbound_cookie_dict[i][0], ' '.join(add), self.response_object.full_domain_name))
            else:
                self.write('Set-Cookie: %s=%s;%s\r\n' % (i, self.response_object.outbound_cookie_dict[i][0], ' '.join(add)))
                    
            self.write('\r\n')
        
        self.write("\r\n")


    def write(self, message):
        self.wfile.write(message.encode())
