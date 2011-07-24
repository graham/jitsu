#! /usr/bin/env python2.5
#not yet
import os
import sys
import time
import gzip

#import io
import socket
import select
import cgi

import threading

class Data(object):
    pass

data_store = Data()
data_store.is_bound = False

USE_EVENTLET = True
try:
    from eventlet import coros, httpc, util
except:
    USE_EVENTLET = False
    
if USE_EVENTLET:
    print('Using Eventlet, this should be awesome.')
    util.wrap_socket_with_coroutine_socket()
else:
    print('No eventlet, that sucks, oh well.')

class JitsuServer(object):
    def __init__(self):
        pass
        
    def start(self):
        self.running = 1
        self.needs_restart = 0
    
        while self.running:
            print('Starting Server...')
            start_time = int(time.time())    
        
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            last_dynamic_code_check = time.time()
        
            pid = os.fork()
        
            if pid == 0:
                print('    Loading...')
                import jitsu
                import jitsu.server
                import jitsu.server.module
            
                from jitsu.server.handler import RequestHandler
                from jitsu.server.jsocket import JitsuHTTPServer
            
            
                httpd = JitsuHTTPServer(server_socket, ('127.0.0.1', 8000), RequestHandler)

                reads = []
                reads.append(sys.stdin)
                reads.append(httpd)
            
                try:
                    print('    Pre-load complete, loading modules', server_socket.getsockname())
                
                    module_list = []
                    httpd.module_list = module_list
                    httpd.job_list = []
                
                    for i in jitsu.server.module.get_all_modules():
                        m = jitsu.server.module.JitsuModule()
                        m.load_module(i)
                        module_list.append(m)
                    
                    if jitsu.server.master_route_object.search('/'):
                        #pass no problem.
                        pass
                    else:
                        # load the default module.
                        m = jitsu.server.module.JitsuModule()
                        m.load_module(['jitsu.apps.default'])
                        module_list.append(m)
            
                    jitsu.server.master_route_object.sort()
                
                    while not self.needs_restart:
                        tmp = select.select(reads, [], [], 0.25)
                    
                        for i in tmp[0]:
                            if i in (httpd, ):
                                x = threading.Thread(target=i.handle_request)
                                x.start()
                            elif i == sys.stdin:
                                tmp = sys.stdin.readline().strip()
                                if tmp == 'restart' or tmp == 'r':
                                    print('restarting...')
                                    self.needs_restart = 1
                                elif tmp == 'pause' or tmp == 'p':
                                    print('pausing for 5 seconds')
                                    for i in range(1, 6):
                                        print(i)
                                        time.sleep(1)
                               
                         
                        if httpd.job_list:
                            x = httpd.job_list.pop()
                            thread = threading.Thread(target=run_job, args=(x,))
                            thread.start()

                except KeyboardInterrupt:
                    print()
                    print("    Shutting Down modules...")                    
                    print("    Shutting Down core...")
                    end_time = int(time.time())
                    print("Server uptime: %.2f minutes" % ((end_time - start_time) / 60.0))
                    self.running = 0
                
                sys.exit(0)
            else:
                try:
                    result = os.waitpid(int(pid), 0)
                    print('result', result)
                    if result[1] == 256:
                        self.running = 0
                except KeyboardInterrupt, ki:
                    self.running = 0
                    print('')
                
            print('Shutdown Complete.')

def run_job(job):
    for i in job:
        pass
    
if __name__=='__main__':  
    x = JitsuServer()
    import jitsu
    jitsu.server_instance = x
    x.start()

