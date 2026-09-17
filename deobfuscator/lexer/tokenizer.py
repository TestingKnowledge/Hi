import re
import time

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

class Lexer:
    RULES = [
        ('COMMENT', r'--\[(=*)\[.*?\]\1\]|--[^\n]*'),
        ('LONGSTRING', r'\[(=*)\[.*?\]\1\]'),
        ('STRING', r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\''),
        ('NUMBER', r'\b\d+(?:\.\d+)?\b'),
        ('KEYWORD', r'\b(local|if|then|else|end|while|do|for|function|return|and|or|not|true|false)\b'),
        ('IDENT', r'\b[a-zA-Z_]\w*\b'),
        ('OP', r'==|~=|\.\.|<=|>=|<|>|\+|-|\*|/|%|\^|=|#'),
        ('PUNC', r'[\[\]\{\}\(\)\.,;]'),
        ('SPACE', r'\s+'),
        ('MISMATCH', r'.')
    ]
    
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start_time = time.time()
        self.tokenize()

    def tokenize(self):
        rules = [(name, re.compile(pattern, re.DOTALL)) for name, pattern in self.RULES]
        pos = 0
        line = 1
        while pos < len(self.source):
            if time.time() - self.start_time > 10:
                raise TimeoutError("Lexer timeout reached.")

            match = None
            for name, regex in rules:
                match = regex.match(self.source, pos)
                if match:
                    val = match.group(0)
                    token_type = 'STRING' if name == 'LONGSTRING' else name

                    if token_type not in ['SPACE', 'COMMENT', 'MISMATCH']:
                        self.tokens.append(Token(token_type, val, line))
                        
                    line += val.count('\n')
                    pos = match.end(0)
                    break
            if not match:
                pos += 1
