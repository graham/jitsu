import socket
import socketserver
import http

class JitsuHTTPServer(socketserver.TCPServer):
    def __init__(self, sock, server_address, RequestHandlerClass):
        socketserver.BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = sock
        self.server_bind()
        self.server_activate()

    def server_bind(self):
        import jitsu.server.server

        if jitsu.server.server.data_store.is_bound:
            pass
        else:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self.server_address)
            jitsu.server.server.data_store.is_bound = True
                
        self.server_address = self.socket.getsockname()
        