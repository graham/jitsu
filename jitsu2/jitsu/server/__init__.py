from jitsu.server.router import Router

master_route_object = Router()

route = master_route_object.route
global_route = master_route_object.global_route
auto_route = master_route_object.auto_route

server_instance = None

from runafter import RunAfter

import jitsu.template.tml

