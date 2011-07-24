from jitsu.server import route, auto_route, global_route

@auto_route('/example/', exclude=['hate'])
class DefaultPage(object):
    @route('')
    def index(self, response, db):
        pass
        
    def list(self, response, db):
        for i in range(10):
            yield 'this is the list<br>'

    @route('serious/')
    def hate(self, response, db):
        return 'you suck.'
    
@auto_route('/example/another/', strict_slash=True)
class AnotherPage(object):
    def index(self, response, db):
        return 'another page'
    @route('create/')
    def create(self, response, db):
        return 'this is the create page'
    def _404(self, response, db):
        return 'That Another page does not exist.'
        
@global_route('/example/foo$')
def foo(request, db):
    return 'this is the foo function, with no object.p'


@auto_route('/example/root/')
class Root(object):
    @route('$')
    def index(self, response, db):
        return 'hi'
    
    def list(self, response, db):
        return 'list'

@auto_route('/example/root/subroot/')
class SubRoot(Root):
    pass