import os

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", 2 * 1024 * 1024)) # 2 MB
MAX_VM_STEPS = int(os.environ.get("MAX_VM_STEPS", 100000))
MAX_VM_STACK_DEPTH = int(os.environ.get("MAX_VM_STACK_DEPTH", 512))
DEOB_TIMEOUT = int(os.environ.get("DEOB_TIMEOUT", 30)) # Seconds
