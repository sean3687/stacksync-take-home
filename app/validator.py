import ast
import re
from typing import List, Tuple

class ScriptValidator:
    # List of forbidden modules and functions
    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'multiprocessing',
        'threading', 'ctypes', 'builtins', 'importlib', 'imp', 'marshal',
        'pickle', 'cPickle', 'cryptography', 'hashlib', 'hmac', 'ssl',
        'tempfile', 'zipfile', 'tarfile', 'ftplib', 'http', 'urllib',
        'requests', 'urllib3', 'paramiko', 'fabric', 'ansible', 'salt',
        'docker', 'kubernetes', 'boto3', 'google.cloud', 'azure'
    }

    # List of forbidden function calls
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', 'input', 'open', 'file', 'raw_input',
        'system', 'popen', 'spawn', 'fork', 'kill', 'exit', 'quit',
        'breakpoint', 'debug', 'trace', 'profile', 'runpy'
    }

    # Maximum script length (in characters)
    MAX_SCRIPT_LENGTH = 10000

    # Maximum number of lines
    MAX_LINES = 200

    @classmethod
    def validate_script(cls, script: str) -> Tuple[bool, str]:
        """
        Validate the Python script for security and correctness.
        Returns (is_valid, error_message)
        """
        # Check script length
        if len(script) > cls.MAX_SCRIPT_LENGTH:
            return False, f"Script exceeds maximum length of {cls.MAX_SCRIPT_LENGTH} characters"

        # Check number of lines
        if script.count('\n') > cls.MAX_LINES:
            return False, f"Script exceeds maximum number of lines ({cls.MAX_LINES})"

        # Check for main() function
        if 'def main()' not in script:
            return False, "Script must contain a main() function"

        try:
            # Parse the script into an AST
            tree = ast.parse(script)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

        # Check for forbidden imports and function calls
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
                if module_name in cls.FORBIDDEN_IMPORTS:
                    return False, f"Forbidden import: {module_name}"

            # Check function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.FORBIDDEN_FUNCTIONS:
                        return False, f"Forbidden function call: {node.func.id}"

        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'__import__\s*\(',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'os\.system\s*\(',
            r'subprocess\s*\.',
            r'\.__dict__',
            r'\.__class__',
            r'\.__bases__',
            r'\.__subclasses__',
            r'\.__globals__',
            r'\.__builtins__',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, script):
                return False, f"Script contains potentially dangerous pattern: {pattern}"

        return True, ""

    @classmethod
    def validate_request(cls, data: dict) -> Tuple[bool, str]:
        """
        Validate the API request data.
        Returns (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Request body must be a JSON object"

        if 'script' not in data:
            return False, "Missing 'script' field in request"

        if not isinstance(data['script'], str):
            return False, "'script' field must be a string"

        if not data['script'].strip():
            return False, "Script cannot be empty"

        return cls.validate_script(data['script']) 