from ..parser.ast import *

class LuaWriter:
    def __init__(self):
        self.indent_level = 0

    def get_indent(self):
        return "    " * self.indent_level

    def write(self, node):
        if isinstance(node, Block):
            lines = []
            for stmt in node.statements:
                result = self.visit(stmt)
                if result:
                    lines.append(self.get_indent() + result)
            return "\n".join(lines)
        return self.visit(node)

    def visit(self, node):
        if isinstance(node, Assignment):
            prefix = "local " if node.is_local else ""
            targets = ", ".join(t.name for t in node.targets)
            if node.values:
                vals = ", ".join(self.visit(v) if v else "nil" for v in node.values)
                return f"{prefix}{targets} = {vals}"
            return f"{prefix}{targets}"
            
        elif isinstance(node, Literal):
            if node.type == 'STRING':
                val = str(node.value)
                if not (val.startswith('"') or val.startswith("'") or val.startswith("[")):
                    return f'"{val}"'
            return str(node.value)
            
        elif isinstance(node, Identifier):
            return node.name
            
        elif isinstance(node, BinaryOp):
            left = self.visit(node.left) if node.left else "nil"
            right = self.visit(node.right) if node.right else "nil"
            return f"{left} {node.op} {right}"
            
        elif isinstance(node, FunctionCall):
            func_name = self.visit(node.func) if node.func else "unknown_func"
            args = ", ".join(self.visit(a) if a else "nil" for a in node.args)
            return f"{func_name}({args})"
            
        elif isinstance(node, ReturnStatement):
            vals = ", ".join(self.visit(v) if v else "nil" for v in node.values)
            return f"return {vals}"
            
        elif isinstance(node, TableConstructor):
            if not node.fields:
                return "{}"
            fields = ", ".join(self.visit(f) if f else "nil" for f in node.fields)
            return f"{{ {fields} }}"
            
        elif isinstance(node, IfStatement):
            cond = self.visit(node.condition) if node.condition else "unknown_cond"
            out = f"if {cond} then\n"
            self.indent_level += 1
            out += self.write(node.if_body) + "\n"
            self.indent_level -= 1
            if node.else_body:
                out += self.get_indent() + "else\n"
                self.indent_level += 1
                out += self.write(node.else_body) + "\n"
                self.indent_level -= 1
            out += self.get_indent() + "end"
            return out
            
        elif isinstance(node, WhileLoop):
            cond = self.visit(node.condition) if node.condition else "unknown_cond"
            out = f"while {cond} do\n"
            self.indent_level += 1
            out += self.write(node.body) + "\n"
            self.indent_level -= 1
            out += self.get_indent() + "end"
            return out
            
        return "-- [Skipped complex or unresolved code block]"
