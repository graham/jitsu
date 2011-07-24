#! /usr/bin/env python2.5
#not yet
import os
import sys
import time
import gzip

#import io
import StringIO as io
import socket
import select
import cgi

import multiprocessing

class Data(object):
    pass

glob_servers = []
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

def start():
    import http
    running = 1
    needs_restart = 0
    import queue
    
    while running:
        print('Starting Server...')
        start_time = int(time.time())    
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        last_dynamic_code_check = time.time()
        
        pid = os.fork()
        
        if pid == 0:
            print('    Loading...')
            import jitsu
            import jitsu.server.module
            import jitsu.server.jobber
            
            from jitsu.server.handler import RequestHandler
            from jitsu.server.jsocket import JitsuHTTPServer
            
            httpd = JitsuHTTPServer(server_socket, ('127.0.0.1', 8000), RequestHandler)
            
            job_queue_parent, job_queue_child = multiprocessing.Pipe()
            httpd.parent_job_queue = job_queue_child
            
            job_process = multiprocessing.Process(target=jitsu.server.jobber.job_runner,
                                        args=(job_queue_parent,) )
            job_process.start()
            
            reads = []
            reads.append(sys.stdin)
            reads.append(httpd)
            
            try:
                print('    Pre-load complete, loading modules', server_socket.getsockname())
                
                modules = jitsu.server.module.get_all_modules()
                module_list = []
                
                for i in modules:
                    command_pipe_parent, command_pipe_child = multiprocessing.Pipe()
                    o = jitsu.server.module.JitsuModule()
                    o.load_module(i, command_pipe_child, None)
                    p = multiprocessing.Process(target=o.run, 
                                                args=(command_pipe_child, None))
                    p.start()
                    module_list.append( ((command_pipe_parent, command_pipe_child), p, o) )
                
                print('    Module Process creation complete.')
                httpd.module_list = module_list
                
                while not needs_restart:
                    tmp = select.select(reads, [], [], 0.25)
                    
                    for i in tmp[0]:
                        if i in (httpd, ):
                            i.handle_request()
                        elif i == sys.stdin:
                            tmp = sys.stdin.readline().strip()
                            if tmp == 'restart' or tmp == 'r':
                                print('restarting...')
                                needs_restart = 1
                            elif tmp == 'pause' or tmp == 'p':
                                print('pausing for 5 seconds')
                                for i in range(1, 6):
                                    print(i)
                                    time.sleep(1)
                                    
                    #while not parent_job_queue.empty():
                    #    job_queue.send(parent_job_queue.recv())
                                                
                for command_pipe, process in module_list:
                    process.terminate()
            except KeyboardInterrupt:
                print()
                print("    Shutting Down modules...")
                for command_pipe, process, obj in module_list:
                    process.terminate()
                    
                print("    Shutting Down core...")
                end_time = int(time.time())
                print("Server uptime: %.2f minutes" % ((end_time - start_time) / 60.0))
                running = 0
                
            job_process.terminate()
            sys.exit(0)
        else:
            try:
                result = os.waitpid(int(pid), 0)
                print('result', result)
                if result[1] == 256:
                    running = 0
            except KeyboardInterrupt, ki:
                running = 0
                print('')
                
        print('Shutdown Complete.')

        
if __name__=='__main__':  
    start()

