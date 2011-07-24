from jitsu.server import route, auto_route, global_route
from jitsu.server.runafter import RunAfter

from jitsu.template.tml import Template
import time

@route('/')
class DefaultPage(object):
    @route('favicon.ico')
    def favicon(self, response, db):
        return ''
        
    @route('')
    def index(self, response, db):
        yield "This is what i found in the test table:<br>" * 10

        for i in db.test.filter():
            yield (i.safe_repr() + '<br>\n')
        yield 'Thats all folks'

        yield "This is a test."

        yield RunAfter()
        

    @route('foo/?$')
    def foo(self, response):
        x = '''
        {% for i in range(10): %}
            my name is {{ name }}<br>
        {% endfor %}
        '''
        x = Template(x)
        return x.render({'name':'graham'})