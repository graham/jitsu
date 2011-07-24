import jitsu.template.blocks as blocks

class IfBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'if ' + x
    
    def _render(self, indent=0, locals=None, globals=None):
        return ''

class ElseIfBlock(blocks.AddPartialBlock):
    def _post_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'elif ' + x
        
class ElseBlock(blocks.AddPartialBlock):
    def _post_block(self, indent=0):
        return ('    ' * indent) + 'else:'
        
    
class TryBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        return ('    ' * indent) + 'try:'
    
class ExceptBlock(blocks.AddPartialBlock):
    def _post_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'except ' + x
        
class FinallyBlock(blocks.AddPartialBlock):
    def _post_block(self, indent=0):
        return ('    ' * indent) + 'finally:'

class ForBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'for ' + x

class WhileBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'while ' + x
        
class UntilBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        x = ' '.join(self.args[1:]).strip()
        if not x.endswith(":"):
            x += ':'
        return ('    ' * indent) + 'while not ' + x
        
class MacroBlock(blocks.StartPartialBlock):
    def _pre_block(self, indent=0):
        return ('    ' * indent) + "def foo():"

class FormBlock(blocks.StartPrettyBlock):
    def begin_block(self, indent=0):
        return "current_form = object()"
    
    def finish_block(self):
        return "current_form"
        
    def render(self):
        return "<form %s %s>" % (self.args, ' '.join(["%s=%s" % (i, self.kwargs[i]) for i in self.kwargs]))
        
    def post_render(self):
        return "</form>"
        
class NiceBox(blocks.StartPrettyBlock):
    def _pre_block(self):
        return '<div class="awesome" id="%s">'
        
class RenderBlock(blocks.BaseBlock):
    def render(self):
        #return 'print("""%%s""" %% ( %s() ), end="", file=_____output) # { with pipe' % self.args[1]
        return 'print >>_____output, """%%s""" %% ( %r ), # { with pipe' % (self.args[1])

        
d = {
    'if':IfBlock,
    'elif':ElseIfBlock,
    'else':ElseBlock,
    'try':TryBlock,
    'except':ExceptBlock,
    'finally':FinallyBlock,
    'for':ForBlock,
    'while':WhileBlock,
    'until':UntilBlock,
    'when':IfBlock,
}

special = {
    'block':MacroBlock,
    'macro':MacroBlock,
    'form':FormBlock,
    'render_block': RenderBlock,
    
}