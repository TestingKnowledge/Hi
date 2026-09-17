from ..parser.ast import *
from ..safety.resource_limits import VMLimits

class SymbolicEvaluator:
    def __init__(self, limits: VMLimits):
        self.limits = limits
        self.steps = 0
        self.partial = False

    def evaluate(self, node, depth=0):
        self.steps += 1
        self.limits.check_limits(self.steps, depth)

        if isinstance(node, Block):
            new_stmts = []
            for stmt in node.statements:
                eval_stmt = self.evaluate(stmt, depth + 1)
                if eval_stmt: new_stmts.append(eval_stmt)
            return Block(new_stmts)

        elif isinstance(node, Assignment):
            eval_vals = [self.evaluate(v, depth + 1) for v in node.values]
            return Assignment(node.is_local, node.targets, eval_vals)

        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left, depth + 1)
            right = self.evaluate(node.right, depth + 1)
            
            if isinstance(left, Literal) and isinstance(right, Literal):
                try:
                    if left.type == 'NUMBER' and right.type == 'NUMBER':
                        if node.op == '+': return Literal(left.value + right.value, 'NUMBER')
                        if node.op == '-': return Literal(left.value - right.value, 'NUMBER')
                        if node.op == '*': return Literal(left.value * right.value, 'NUMBER')
                        if node.op == '/' and right.value != 0: return Literal(left.value / right.value, 'NUMBER')
                        if node.op == '%' and right.value != 0: return Literal(left.value % right.value, 'NUMBER')
                        if node.op == '^': return Literal(left.value ** right.value, 'NUMBER')
                    
                    if node.op == '..':
                        l_str = str(left.value).strip("\"'[]=")
                        r_str = str(right.value).strip("\"'[]=")
                        return Literal(f'"{l_str}{r_str}"', 'STRING')
                except Exception:
                    self.partial = True
            
            return BinaryOp(left, node.op, right)

        elif isinstance(node, TableConstructor):
            eval_fields = [self.evaluate(f, depth + 1) for f in node.fields]
            return TableConstructor(eval_fields)

        elif isinstance(node, IfStatement):
            cond = self.evaluate(node.condition, depth + 1)
            if_body = self.evaluate(node.if_body, depth + 1)
            else_body = self.evaluate(node.else_body, depth + 1) if node.else_body else None
            return IfStatement(cond, if_body, else_body)

        elif isinstance(node, WhileLoop):
            cond = self.evaluate(node.condition, depth + 1)
            body = self.evaluate(node.body, depth + 1)
            return WhileLoop(cond, body)

        elif isinstance(node, ReturnStatement):
            eval_vals = [self.evaluate(v, depth + 1) for v in node.values]
            return ReturnStatement(eval_vals)

        elif isinstance(node, FunctionCall):
            self.partial = True 
            eval_args = [self.evaluate(arg, depth + 1) for arg in node.args]
            return FunctionCall(node.func, eval_args)

        return node
