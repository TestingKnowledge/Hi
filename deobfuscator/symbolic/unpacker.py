import re
import ast

class StringPoolUnpacker:
    def __init__(self, source: str):
        self.source = source

    def unpack(self) -> str:
        """
        Safely extracts the constant string table 'U' and resolves 
        obfuscated string references without executing untrusted code.
        """
        try:
            # 1. Regex to locate the global string array 'local U = { ... }'
            match = re.search(r'local\s+U\s*=\s*(\{.*?\})\s*(?:local|for|do|return)', self.source, re.DOTALL)
            if not match:
                return self.source

            table_literal = match.group(1)
            
            # Clean up lua table syntax to make it safe for python ast evaluation if needed,
            # or extract individual quoted strings using standard regex findall.
            raw_strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\'', table_literal)
            
            # Flatten matched groups
            extracted_strings = [s[0] or s[1] for s in raw_strings]
            
            if not extracted_strings:
                return self.source

            # 2. Replace obfuscated table access patterns like S(1), S(2) with actual decoded literals
            # We find occurrences of S(expr) where expr evaluates mathematically.
            def replace_s_call(m):
                expr = m.group(1)
                try:
                    # Safely evaluate simple offset arithmetic inside S(...) e.g., S(-844356+860808)
                    index = eval(expr, {"__builtins__": {}}, {})
                    # Lua tables are 1-indexed, Python is 0-indexed
                    py_index = index - 1
                    if 0 <= py_index < len(extracted_strings):
                        val = extracted_strings[py_index]
                        return f'"{val}"'
                except Exception:
                    pass
                return m.group(0)

            # Match pattern like S(123) or S(number + number)
            unpacked_source = re.sub(r'\bS\(\s*([0-9\+\-\*\/\(\)]+)\s*\)', replace_s_call, self.source)
            
            return unpacked_source
        except Exception as e:
            # Fallback gracefully if the pattern doesn't match standard layouts
            return self.source
