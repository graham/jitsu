import re
import types

class RouteObject(object):
    def __init__(self):
        self.base_routes = []
        self.sub_routes = {}
        self.klass = None

class Router(object):
    def __init__(self):
        self.routes = {}
        self.route_table = []
        
    def sort(self):
        self.route_table = list(self.routes.keys())
        self.route_table.sort()
        self.route_table.reverse()

    def route(self, is_global=0, auto_route=0, auto_strict_slash=0, auto_exclude=[], *args):
        def test(routable):
            if type(routable) == type:
                ro = RouteObject()

                for i in args:
                    ro.base_routes.append(i)
                    ro.klass = routable
                    
                    if i in self.routes:
                        print('*'*40)
                        print('Attempting to overwrite path: %s' % i)
                        print('*'*40)
                    self.routes[i] = ro
                    
                if auto_route:
                    for i in dir(routable):
                        if i.startswith('_'):
                            pass
                        elif i in auto_exclude:
                            pass
                        else:
                            f = getattr(routable, i)
                            if type(f) == types.FunctionType:
                                if auto_strict_slash:
                                    ro.sub_routes[i+'/$'] = f
                                else:
                                    ro.sub_routes[i+'/?$'] = f
                                    
                return routable
                
            elif type(routable) == types.FunctionType:
                ro = RouteObject()
                ro.klass = routable
                if is_global:
                    for i in args:
                        self.routes[i] = ro
                routable._page_route = args
                return routable
                
            else:
                print('No idea how to handle routable: %s' % routable)
                return routable
                
        return test
    
    def global_route(self, *args):
        return self.route(is_global=1, *args)
    
    def auto_route(self, strict_slash=0, exclude=[], *args):
        return self.route(auto_route=1, auto_strict_slash=strict_slash, auto_exclude=exclude, *args)
        
    def unregister(self, route):
        self.routes.pop(route)
    
    def root_search(self, s):
        for i in self.route_table:
            m = re.match(i, s)
            if m:
                match = m
                route_object = self.routes[i]
                rest = s[match.end():]
                
                if type(route_object.klass) == type:
                    return (route_object.klass, match)
                else:
                    return None
        return None
                
    def search(self, s):
        for i in self.route_table:
            m = re.match(i, s)
            if m:
                match = m
                route_object = self.routes[i]
                rest = s[match.end():]
                
                if type(route_object.klass) == type:
                    # This is so flipping ugly, REWRITE
                    for i in route_object.sub_routes:
                        if i == '' and i != rest:
                            continue;
                        
                        m = re.match(i, rest)
                        if m:
                            return (route_object.sub_routes[i], route_object.klass, match)
                    
                    for i in dir(route_object.klass):
                        if not i.startswith('__'):
                            if getattr(route_object.klass, i, None):
                                if type(getattr(route_object.klass, i)) == types.FunctionType:
                                    function = getattr(route_object.klass, i)
                                    if getattr(function, '_page_route', None):
                                        sub_route = getattr(function, '_page_route')
                                        for j in sub_route:
                                            if j == '' and j != rest:
                                                continue;
                                                    
                                            m = re.match(j, rest)
                                            if m:
                                                route_object.sub_routes[j] = function
                                                return (function, route_object.klass, m)
                else:
                    return (route_object.klass, None, match)
                    
        return None
    


# @auto_route('/other/')
# class AdminPage(object):
#     @route('')
#     def index(self):
#         print('Welcome to the index!', self)
#     def list(self):
#         print('hello world of lists!')

# /admin/users/.*
# /admin/people/.*
# /admin/10/list/
# /admin/(users|people|danger)/[0-9]+/.*
# 
# @route('/admin/users/')
# class AdminUsersPage(object):
#     def __init__(self):
#         self.x = 10
# 
#     @route('(\d+)/list/')
#     def list(self):
#         print('Welcome to the list!', self)
#         print('x:', self.x)
#     
#     @route('create/')
#     def create(self):
#         print('Welcome to the create!', self)
#     
#     @route('delete_user/')
#     def delete(self):
#         print('Welcome to the delete!', self)
# 
# @global_route('/home')
# def home_page(*args):
#     print('this is the home page.')
# 
# the_route.sort()
# for i in the_route.route_table:
#     print('Route: ', i, ' Object:', the_route.routes[i])
# print('--', '\n')
# 
# print('\n\n')
# 
# route = '/admin/users/31/list/'
# method, klass = the_route.search(route)
# 
# y = klass()
# method(y)
# 
# print(AdminPage._sub_routes)
# route = '/other/index'
# print(the_route.search(route))