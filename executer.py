import os
import subprocess
import webbrowser
import sys
import threading
import time
import json
from skills import web, system, ui, vision

class Executor:
    def __init__(self):
        # Explicitly forbidden patterns
        self.forbidden_patterns = [
            "rm -rf", "format ", "del /", "rd /", "shutil.rmtree", 
            "os.remove", "os.rmdir", "os.unlink", 
            "reg edit", "reg add", "reg delete", "reg copy", 
            "mkfs", "fdisk", " dd "
        ]

    def is_safe(self, code):
        code_lower = code.lower()
        for pattern in self.forbidden_patterns:
            if pattern in code_lower:
                return False, pattern
        return True, None

    def execute(self, code):
        safe, reason = self.is_safe(code)
        if not safe:
            return f"Safety Protocol: Command blocked due to restricted pattern '{reason}'."

        # Pre-process code to handle semicolons for multi-line statements
        # This fixes issues like "import os; with open(...) as f: pass"
        if ";" in code and "\n" not in code:
            code = code.replace("; ", "\n").replace(";", "\n")

        # Define the execution context (variables available to the code)
        context = {
            "os": os,
            "subprocess": subprocess,
            "webbrowser": webbrowser,
            "time": time,
            "json": json,
            "web": web,
            "system": system,
            "ui": ui,
            "vision": vision,
            "print": print,
            # Self-reference for module lookups
            "skills.system": system,
            "skills.web": web,
            "skills.ui": ui,
            "skills.vision": vision
        }

        # Capture stdout to return print statements
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        
        try:
            # Execute in restricted scope with stdout capture
            with redirect_stdout(f):
                exec(code, context)
            
            output = f.getvalue()
            return output if output else "Execution successful."
            
        except Exception as e:
            return f"Error executing code: {e}"
