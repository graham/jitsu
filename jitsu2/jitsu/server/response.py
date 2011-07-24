import time
import re
import jitsu
import jitsu.template.tml
from jitsu.server.runafter import RunAfter

class Response:
    def __init__(self, url, 
                       raw_url, 
                       form_data, 
                       cookie_data, 
                       environ, 
                       ip, 
                       secure, 
                       request_hostname, 
                       request_type,
                       rethrow=False,
                       get_form_data={},
                       post_form_data={},
                       server=None
                       ):
                       
        self.start_time = time.time()
                     
        self.server = server
        self.url = url
        self.raw_url = raw_url
        self.form_data = form_data
        self.inbound_cookie_data = cookie_data
        self.outbound_cookie_dict = {}
        self.environ = environ
        self.ip = ip
        self.secure = secure
        self.request_hostname = request_hostname
        self.request_type = request_type
        
        self.get_form_data = get_form_data
        self.post_form_data = post_form_data
        
        self.outbound_cookie_data = {}
        self.headers_dict = {}
        
        self.content_type = 'text/html'
        self.max_age = 65535
        
        self.return_code = (200, 'OK')
        self.payload = ''
        
        
        self.flush_headers = False
        self.finished = False
        
    def render_headers(self):
        self.headers_dict['Date'] = '%s' % time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        self.headers_dict['Server'] = 'jitsu'
        self.headers_dict['Connection'] = "close"
        self.headers_dict['Content-Type'] = '%s' % self.content_type
        self.headers_dict['Keep-Alive'] = 'timeout=5, max=9998'
        #self.headers_dict['Cache-Control'] = 'max-age=%i' % self.max_age
        #self.headers_dict['Content-Length'] = len(self.payload)

        self.outbound_cookie_dict = {}
        for i in self.outbound_cookie_data:
            value, path, expire = self.outbound_cookie_data[i]
            if expire == -1:
                t = time.gmtime(0)
            else:
                t = time.gmtime(time.time() + expire)

            self.outbound_cookie_dict[i] = (value, {'path':path, 'expires':time.strftime("%a, %d-%b-%Y %H:%M:%S GMT", t)})

    def render(self):    
        import jitsu.server
        import jitsu.orm


        x = jitsu.server.master_route_object.search(self.url)

        if x:
            method, klass, match = x

            if klass:
                obj = klass()
                ret = None
                
                if method.__code__.co_argcount == 1:
                    # this is here just so you can fire off something quick if you want.
                    self.pre_render_page_object(obj)
                    ret = method(obj)
                    
                elif method.__code__.co_argcount == 2:
                    # looks like they don't want a database so don't even try
                    self.pre_render_page_object(obj)
                    ret = method(obj, self)
                    
                else:
                    self.db = jitsu.orm.connect_sqlite("mydb.db")
                    self.pre_render_page_object(obj)
                    ret = method(obj, self, self.db)

                if ret == None:
                    # here is were we are going to render the template.
                    ret = 'This should be template data! Woot!'
            
                self.post_render_page_object(obj)

                return ret
            else:
                return method(self, self.db)
        else:
            x = jitsu.server.master_route_object.root_search(self.url)
            if x:
                klass, match = x
                obj = klass
                method = getattr(klass, '_404', None)
                if method:
                    return method(obj, self, self.db)
                else:
                    pass
                    
        return 'The URL you requested did not match any valid routes, deploying ninjas.'
    
    def pre_render_page_object(self, obj):
        if (getattr(obj, '_get_db', False)):
            self.db = obj._get_db(request, self.db)
        
    def post_render_page_object(self, obj):
        import time
        print(time.asctime(), ("%.6f" % (time.time()-self.start_time)).ljust(10), str(self.get_form_data).ljust(20), str(self.post_form_data).ljust(20), self.url.ljust(20))
        
        
    def finish(self):
        pass

