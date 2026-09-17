import time
from .ast import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.start_time = time.time()

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None, expected_value=None):
        tok = self.peek()
        if tok and (expected_type is None or tok.type == expected_type) and (expected_value is None or tok.value == expected_value):
            self.pos += 1
            return tok
        return None

    def parse(self):
        stmts = []
        while self.peek():
            if time.time() - self.start_time > 10:
                break
                
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            else:
                self.pos += 1
        return Block(stmts)

    def parse_statement(self):
        if self.consume('KEYWORD', 'return'):
            values = []
            while True:
                val = self.parse_expression()
                if not val: break
                values.append(val)
                if not self.consume('PUNC', ','): break
            return ReturnStatement(values)
            
        if self.consume('KEYWORD', 'if'):
            condition = self.parse_expression()
            self.consume('KEYWORD', 'then')
            if_body = self.parse()
            else_body = None
            if self.consume('KEYWORD', 'else'):
                else_body = self.parse()
            self.consume('KEYWORD', 'end')
            return IfStatement(condition, if_body, else_body)

        if self.consume('KEYWORD', 'while'):
            condition = self.parse_expression()
            self.consume('KEYWORD', 'do')
            body = self.parse()
            self.consume('KEYWORD', 'end')
            return WhileLoop(condition, body)

        if self.consume('KEYWORD', 'local'):
            return self.parse_assignment(is_local=True)
            
        saved = self.pos
        ident = self.consume('IDENT')
        if ident and self.consume('OP', '='):
            self.pos = saved
            return self.parse_assignment(is_local=False)
        self.pos = saved
        
        expr = self.parse_expression()
        if isinstance(expr, FunctionCall):
            return expr
        return None

    def parse_assignment(self, is_local):
        targets = []
        while True:
            t = self.consume('IDENT')
            if not t: break
            targets.append(Identifier(t.value))
            if not self.consume('PUNC', ','): break
            
        values = []
        if self.consume('OP', '='):
            while True:
                val = self.parse_expression()
                if not val: break
                values.append(val)
                if not self.consume('PUNC', ','): break
                
        return Assignment(is_local, targets, values)

    def parse_expression(self):
        left = self.parse_primary()
        if not left: return None
        
        while True:
            op = self.consume('OP')
            if op:
                right = self.parse_primary()
                if right:
                    left = BinaryOp(left, op.value, right)
                else:
                    break
            else:
                break
        return left

    def parse_primary(self):
        tok = self.peek()
        if not tok: return None
        
        if tok.type == 'NUMBER':
            self.pos += 1
            return Literal(float(tok.value) if '.' in tok.value else int(tok.value), 'NUMBER')
        elif tok.type == 'STRING':
            self.pos += 1
            return Literal(tok.value, 'STRING')
            
        elif tok.type == 'PUNC' and tok.value == '{':
            self.pos += 1
            fields = []
            while self.peek() and not self.consume('PUNC', '}'):
                start_pos = self.pos
                field = self.parse_expression()
                if field: fields.append(field)
                self.consume('PUNC', ',')
                self.consume('PUNC', ';')
                if self.pos == start_pos:
                    self.pos += 1
            return TableConstructor(fields)
            
        elif tok.type == 'IDENT':
            self.pos += 1
            ident = Identifier(tok.value)
            if self.consume('PUNC', '('):
                args = []
                while self.peek() and not self.consume('PUNC', ')'):
                    start_pos = self.pos
                    arg = self.parse_expression()
                    if arg: args.append(arg)
                    self.consume('PUNC', ',')
                    if self.pos == start_pos:
                        self.pos += 1
                return FunctionCall(ident, args)
            return ident
        return None
