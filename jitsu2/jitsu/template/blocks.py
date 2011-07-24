import jitsu

class BaseBlock(object):
    does_indent = 1
    start_block = 0
    mid_block = 0
    end_block = 0
    slurp = 0
    
    def __init__(self, string, command=None, args=None, kwargs=None):
        self.string = string
        self.command = command
        
        self.args = args or []
        self.kwargs = kwargs or {}
        
        #print('Args: %r' % args)
        if args:
            if len(args) == 1:
                args = args[0]

        tmp_args = jitsu.safe_split(args, ',', '(', ')')
        for i in tmp_args:
            if '=' in i:
                j = i.split('=', 1)
                self.kwargs[j[0]] = j[1]
            else:
                self.args
        
    def modify(self, command_stack):
        pass
        
    def _pre_block(self, indent=0):
        return ''
    
    def _begin_block(self, indent=0):
        return ('    '*indent) + self.begin_block()

    def begin_block(self):
        return ''
        
    def _finish_block(self, indent=0):
        return ('    '*indent) + self.finish_block()
        
    def finish_block(self, indent=0):
        return ''
    
    def _post_block(self, indent=0):
        return ''
    
    def _render(self, indent=0, locals=None, globals=None):
        return ('    ' * indent) + self.render()
        
    def _post_render(self, indent=0, locals=None, globals=None):    
        return ('    ' * indent) + self.post_render()

    def render(self):
        return self.string
        
    def post_render(self):
        return ''
    
class EndBlock(BaseBlock):
    end_block = 1
    def _render(self, indent=0, locals=None, globals=None):
        return  ''
    
class StaticBlock(BaseBlock):
    def _render(self, indent=0, locals=None, globals=None):
        if self.string == '':
            return ''
        else:
            r = self.render()
            if r:
                #return '%sprint("""%%s""" %% ( %r ), end="", file=_____output) # { with pipe' % ('    ' * indent, r)
                return '%sprint >>_____output, """%%s""" %% ( %r ), # { with pipe' % ('    ' * indent, r)
            else:
                return ''

class EnclosedBlock(BaseBlock):
    def _render(self, indent=0, locals=None, globals=None):
        import jitsu.template.tml
        t = jitsu.template.tml.Template(self.string)
        t.compile()
        l = []
        for i in t.template_code:
            l.append( ('    ' * indent) + i)
        return '\n'.join(l)
    
class StartPartialBlock(BaseBlock):
    start_block = 1
    slurp = 1
    def _render(self, indent=0, locals=None, globals=None):
        return ''

class AddPartialBlock(BaseBlock):
    mid_block = 1
    slurp = 1
    def _render(self, indent=0, locals=None, globals=None):
        return ''

class Command(BaseBlock):
    pass

class EvalBlock(BaseBlock):
    def _render(self, indent=0, locals=None, globals=None):
        if '|' in self.string:
            ## Replace in 3.0 python3k p3k
            # evaller, *pipe = self.string.split('|')
            evaller, pipe = self.string.split("|", 1)
            pipe = pipe.split('|')

            s = "str(%s)" % evaller
            for i in pipe:
                s = "FILTER_%s(%s)" % (i.strip(), s)

            ## Replace in 3.0 python3k p3k
            #return '%sprint("""%%s""" %% ( %s ), end="", file=_____output) # { with pipe' % ('    ' * indent, s)
            return '%sprint >>_____output, """%%s""" %% ( %r ), # { with pipe' % ('    ' * indent, s)
            
        else:
            r = self.render()
            if r:
            ## Replace in 3.0 python3k p3k            
                #return '%sprint("""%%s""" %% ( %s ), end="", file=_____output)' % ('    ' * indent, self.render())
                return '%sprint >>_____output, """%%s""" %% ( %r ), # { with pipe' % ('    ' * indent, self.render())
            else:
                return ''
            
    
class UnknownBlock(BaseBlock):
    pass
    
class StartPrettyBlock(StartPartialBlock):
    does_indent = 0
    start_block = 1
    slurp = 1

    def _render(self, indent=0, locals=None, globals=None):
        r = self.render()
        if r:
            #return '%sprint("""%%s""" %% ( %r ), end="", file=_____output) # { with pipe' % ('    ' * indent, r)
            return '%sprint >>_____output, """%%s""" %% ( %r ), # { with pipe' % ('    ' * indent, r)
            
        else:
            return ''
