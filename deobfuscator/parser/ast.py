class Node: pass

class Block(Node):
    def __init__(self, statements):
        self.statements = statements

class Assignment(Node):
    def __init__(self, is_local, targets, values):
        self.is_local = is_local
        self.targets = targets
        self.values = values

class Literal(Node):
    def __init__(self, value, type_):
        self.value = value
        self.type = type_

class Identifier(Node):
    def __init__(self, name):
        self.name = name

class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class FunctionCall(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args

class IfStatement(Node):
    def __init__(self, condition, if_body, else_body=None):
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body

class WhileLoop(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class TableConstructor(Node):
    def __init__(self, fields):
        self.fields = fields

class ReturnStatement(Node):
    def __init__(self, values):
        self.values = values
