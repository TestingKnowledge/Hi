import time
from dataclasses import dataclass, field
from typing import List

from .lexer import Lexer
from .parser import Parser
from .symbolic import SymbolicEvaluator, StringPoolUnpacker
from .reconstruction import LuaWriter
from .safety.resource_limits import VMLimits

@dataclass
class DeobResult:
    source: str
    complete: bool
    stages: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class DeobfuscationPipeline:
    def __init__(self):
        self.limits = VMLimits()

    def run(self, source: str) -> DeobResult:
        self.limits.start_time = time.time()
        result = DeobResult(source="", complete=False)
        
        try:
            result.stages.append("Source validated")
            
            # 1. Run Static String Pool Unpacking First
            unpacker = StringPoolUnpacker(source)
            unpacked_source = unpacker.unpack()
            result.stages.append("String-pool table decrypted")

            lexer = Lexer(unpacked_source)
            result.stages.append("Lexer completed")

            parser = Parser(lexer.tokens)
            ast = parser.parse()
            result.stages.append("AST constructed")

            evaluator = SymbolicEvaluator(self.limits)
            optimized_ast = evaluator.evaluate(ast)
            
            result.stages.append("VM constant folding completed")

            writer = LuaWriter()
            reconstructed = writer.write(optimized_ast)
            result.stages.append("Payload reconstruction completed")

            result.source = reconstructed
            result.complete = not evaluator.partial

        except TimeoutError:
            result.warnings.append("TIMEOUT")
            result.source = "-- Analysis halted: DEOB_TIMEOUT reached.\n" + result.source
        except RuntimeError as e:
            result.warnings.append("LIMIT_REACHED")
            result.source = f"-- Analysis halted: {str(e)}.\n" + result.source
        except Exception as e:
            result.warnings.append(f"FATAL_ERROR: {str(e)}")
            result.source = "-- Analysis failed due to malformed script structure."

        return result
