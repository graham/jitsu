from jitsu.server import route, auto_route, global_route
from jitsu.server.runafter import RunAfter

from jitsu.template.tml import Template

@route('/admin/tools/')
class AdminToolsPage(object):
        
    @route('restart/')
    def index(self, response, db):
        yield 'Attempting restart'
        yield RunAfter()
        
        import jitsu
        server_instance = jitsu.server_instance
        server_instance.needs_restart = 1

        
