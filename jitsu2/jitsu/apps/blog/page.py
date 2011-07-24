from jitsu.server import route, auto_route

@auto_route('/blog/')
class BlogMainPage(object):
    @route('$')
    def index(self, response, db):
        return 'Here are a bunch of blog entries'