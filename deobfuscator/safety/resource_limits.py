import time
import config
from dataclasses import dataclass

@dataclass
class VMLimits:
    max_steps: int = config.MAX_VM_STEPS
    max_stack_depth: int = config.MAX_VM_STACK_DEPTH
    timeout: int = config.DEOB_TIMEOUT
    start_time: float = 0.0

    def check_limits(self, step_count: int, depth: int):
        if time.time() - self.start_time > self.timeout:
            raise TimeoutError("DEOB_TIMEOUT")
        if step_count > self.max_steps:
            raise RuntimeError("MAX_VM_STEPS_REACHED")
        if depth > self.max_stack_depth:
            raise RuntimeError("MAX_STACK_DEPTH_REACHED")
