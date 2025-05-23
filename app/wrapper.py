import sys
import io
import json
from contextlib import redirect_stdout

def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            'error': 'No script file provided'
        }))
        sys.exit(1)

    script_path = sys.argv[1]
    
    try:
        with open(script_path, 'r') as f:
            script = f.read()

        # Create a new namespace for execution
        namespace = {}
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            exec(script, namespace)
        
        # After exec, call main() and capture its return value
        if 'main' in namespace and callable(namespace['main']):
            try:
                result = namespace['main']()
            except Exception as e:
                print(json.dumps({
                    'error': f'Error in main(): {str(e)}',
                    'stdout': stdout_capture.getvalue()
                }))
                sys.exit(1)
        else:
            print(json.dumps({
                'error': 'No main() function found in the script',
                'stdout': stdout_capture.getvalue()
            }))
            sys.exit(1)
        
        # Print the result in JSON format as the last line
        print(json.dumps({
            'result': result,
            'stdout': stdout_capture.getvalue()
        }))
        
    except Exception as e:
        print(json.dumps({
            'error': str(e),
            'stdout': stdout_capture.getvalue() if 'stdout_capture' in locals() else ''
        }))
        sys.exit(1)

if __name__ == '__main__':
    main() 