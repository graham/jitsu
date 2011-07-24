import jitsu.template.filters
import jitsu.template.blocks as blocks
import jitsu.template.core_blocks as core_blocks

import codeop
import re
import sys
#import io
import StringIO as io

CC = ("{", "}")

CONDITIONS = ['if', 'try']
ADD_CONDITIONS = ['elif', 'else', 'except', 'finally']
LOOPS = ['while', 'for']

d = {}

EXEC = "$"
CONDITION = "%"
PREEXEC = "*"
COMMENT = "#"
EVAL = "{"
OP_EVAL = "}"

for i in (EXEC, CONDITION, PREEXEC, COMMENT, EVAL):
    d[i] = re.compile("\%s\%s" % (i, CC[1]), re.MULTILINE)

START_COMMAND = re.compile("%s(%s)" % (CC[0], '|'.join(['\%s' % i for i in d.keys()])), re.MULTILINE)

class Template(object):
    is_block = 1
    def __init__(self, text='', name='', commands=None, filters=None):
        self._____output = io.StringIO()
        self.text = text
        self.name = name
        self.been_parsed = 0
        self.globals = {'_____output':self._____output}

        self.globals.update(**jitsu.template.filters.FILTERS)
        
        if filters:
            self.globals.update(**filters)

        self.commands = {}
        
        self.code_blocks = []
        
    def parse(self, predent=''):
        if self.been_parsed:
            return
        else:
            self.been_parsed = 1
            self.data = self.do_parse(self.text, predent=predent)
        
    def compile(self):
        self.parse()
        
        self.data = []
        
        indent_level = 0
        for i in self.code_blocks:
            self.data.append(i._pre_block(indent=indent_level))

            if i.start_block and i.does_indent:
                indent_level += 1
                
            bb = i._begin_block(indent=indent_level)
            if bb.strip():
                self.data.append(bb)

            self.data.append(i._render(indent=indent_level))

            if i.end_block and i.does_indent:
                indent_level -= 1
                
            if indent_level < 0:
                indent_level = 0
                
            if i.mid_block:
                self.data.append(i._post_block(indent=indent_level-1))
            else:
                self.data.append(i._post_block(indent=indent_level))
                
        result = []
        for i in self.data:
            if i == '':
                pass
            else:
                result.append(i)
        
        self.template_code = result

    def render(self, locals={}):
        self.compile()
        result = self.template_code
        result = '\n'.join(result)
        try:
            exec(result, self.globals, locals)
        except Exception, e:
            import jitsu.server.util
            x = jitsu.server.util.steal_stack_trace()
            return x
        return self.globals['_____output'].getvalue()

    def do_parse(self, data, predent=1):
        code_segment = []
        current_index = 0
        command_stack = []
        
        if predent:
            command_stack.append(predent)
        
        sub_templates = []
        
        block_name = ''
        block_object = None
        special_start = 0
        matches = START_COMMAND.finditer(data)
        
        count = 0
        
        for i in matches:
            slurp_newline = 0
            count += 1
            command_char = data[i.span()[0]+1]

            if command_char in d:
                new_command_char = command_char
                if command_char == EVAL:
                    new_command_char = OP_EVAL
            
                end_comp = re.compile("\%s\%s" % (new_command_char, CC[1]), re.MULTILINE)
            
                end_match = end_comp.search(data, pos=i.span()[1])

                if not end_match:
                    raise Exception("Balls")

                begin = i.span()[0]
                start = i.span()[1]
                end = end_match.span()[0]
                after = end_match.span()[1]
            
                prev_static = data[current_index:i.span()[0]]
                
                content = data[start:end]
                content = content.strip()
                index_of_space = content.find(' ')
                index_of_open_paren = content.find('(')
                
                nkwargs = {}
                
                if index_of_open_paren == -1:
                    command = content.split(" ")[0]
                    args = content.split(" ")
                elif index_of_open_paren != -1:
                    if index_of_space == -1 or (index_of_open_paren < index_of_space):
                        command = content.split("(", 1)[0]
                        args = content.split("(", 1)[1].rstrip(')')
                    else:
                        command = content.split(" ")[0]
                        args = content.split(" ")

                        
                if len(command_stack) == 0:
                    self.code_blocks.append(blocks.StaticBlock(prev_static, command=command, args=args, kwargs=nkwargs))
                
                    if command_char == EVAL:
                        self.code_blocks.append(blocks.EvalBlock(content, command=command, args=args, kwargs=nkwargs))
                    elif command_char == CONDITION:
                        if command in core_blocks.special:
                            new = core_blocks.special[command](content, command=command, args=args, kwargs=nkwargs)

                            if new.start_block:
                                block_name = command
                                special_start = after
                                block_object = new
                                command_stack.append(new)
                                self.code_blocks.append(new)
                            else:
                                self.code_blocks.append(new)
                        elif command in core_blocks.d:
                            if prev_static.strip() == '':
                                self.code_blocks = self.code_blocks[:-1]
                            
                            new = core_blocks.d[command](content, command=command, args=args, kwargs=nkwargs)
                            
                            self.code_blocks.append(new)
                            
                        elif command.startswith("end"):
                            rest = None
                            if prev_static.strip(' ') == '':
                                self.code_blocks, rest = self.code_blocks[:-1], self.code_blocks[-1]

                            self.code_blocks.append(blocks.EndBlock('', command=command, args=args, kwargs=nkwargs))
                        else:
                            print("Unknown command: %s" % command)
                    else:
                        print("Unknown command type", command_char)
                else:
                    prev_block_content = data[special_start:begin]
                    
                    if command_char == CONDITION:
                        if command in core_blocks.special:
                            self.code_blocks.append(blocks.EnclosedBlock(prev_block_content, command=command, args=args, kwargs=nkwargs))
                            block_name = command
                            block_object = core_blocks.special[command](content, command=command, args=args, kwargs=nkwargs)
                            special_start = after

                            if block_object.start_block:
                                command_stack.append(block_object)

                            self.code_blocks.append(block_object)

                        elif command in core_blocks.d:
                            new = core_blocks.d[command](content, command=command, args=args, kwargs=nkwargs)

                            self.code_blocks.append(new)

                        elif command.startswith("end"):
                            self.code_blocks.append(blocks.EnclosedBlock(prev_block_content, command=command, args=args, kwargs=nkwargs))
                            obj = command_stack.pop()

                            special_start = after
                            self.code_blocks.append(blocks.StaticBlock(obj.post_render()+'\n'))
                            self.code_blocks.append(blocks.EvalBlock(obj._finish_block()))
                            self.code_blocks.append(blocks.EndBlock(''))
                            
                    else:
                        pass # because we don't care until the block is done.
                
            
            
            current_index = end_match.span()[1]
            
        if current_index <= len(data):
            self.code_blocks.append(blocks.StaticBlock(data[current_index:]))
            
        for i in self.code_blocks:
            pass
            
