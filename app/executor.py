import os
import tempfile
import subprocess
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CodeExecutor:
    def __init__(self, config_path):
        self.config_path = config_path
        self.temp_dir = Path("/tmp/scripts")
        self.temp_dir.mkdir(exist_ok=True)
        self.wrapper_path = os.path.join(os.path.dirname(__file__), 'wrapper.py')
        
        # Verify files exist
        logger.info(f"Config path: {self.config_path}")
        logger.info(f"Wrapper path: {self.wrapper_path}")
        logger.info(f"Config exists: {os.path.exists(self.config_path)}")
        logger.info(f"Wrapper exists: {os.path.exists(self.wrapper_path)}")

    def execute(self, script):
        # Create a temporary file for the script
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=self.temp_dir,
            delete=False
        ) as temp_file:
            temp_file.write(script)
            temp_file.flush()
            script_path = temp_file.name

        try:
            # First, let's try without nsjail to see if the script works
            logger.info("Testing script execution without nsjail first...")
            test_cmd = ['/usr/local/bin/python3', self.wrapper_path, script_path]
            test_process = subprocess.Popen(
                test_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            test_stdout, test_stderr = test_process.communicate(timeout=5)
            logger.info(f"Direct execution - Return code: {test_process.returncode}")
            logger.info(f"Direct execution - Stdout: {test_stdout}")
            logger.info(f"Direct execution - Stderr: {test_stderr}")
            
            if test_process.returncode == 0:
                # If direct execution works, try with nsjail
                logger.info("Direct execution successful, now trying with nsjail...")
                
                # Prepare the command to run the script in nsjail
                cmd = [
                    '/usr/local/bin/nsjail',
                    '--config', self.config_path,
                    '--',
                    '/usr/local/bin/python3',
                    self.wrapper_path,
                    script_path
                ]
                
                logger.info(f"Executing command: {' '.join(cmd)}")

                # Execute the script in nsjail
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                try:
                    stdout, stderr = process.communicate(timeout=15)
                    logger.info(f"Nsjail execution - Return code: {process.returncode}")
                    logger.info(f"Nsjail execution - Stdout: {stdout}")
                    logger.info(f"Nsjail execution - Stderr: {stderr}")
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    return {
                        'error': 'Execution timed out',
                        'stdout': ''
                    }

                # Check if the execution was successful
                if process.returncode != 0:
                    return {
                        'error': f'Nsjail execution failed: {stderr}',
                        'stdout': stdout
                    }

                # Try to parse the result from stdout
                try:
                    # Filter out nsjail log messages and get the JSON result
                    lines = stdout.strip().split('\n')
                    json_line = None
                    
                    # Look for the JSON result (should be the last line that starts with {)
                    for line in reversed(lines):
                        if line.strip().startswith('{'):
                            json_line = line.strip()
                            break
                    
                    if json_line:
                        result = json.loads(json_line)
                        return result
                    else:
                        return {
                            'error': 'No valid JSON result found in output',
                            'stdout': stdout
                        }
                        
                except json.JSONDecodeError as e:
                    return {
                        'error': f'Failed to parse execution result: {str(e)}',
                        'stdout': stdout
                    }
            else:
                # If even direct execution fails, return that error
                return {
                    'error': f'Script execution failed: {test_stderr}',
                    'stdout': test_stdout
                }

        except Exception as e:
            logger.exception(f"Execution error: {str(e)}")
            return {
                'error': f'Execution error: {str(e)}',
                'stdout': ''
            }
        finally:
            # Clean up the temporary file
            try:
                os.unlink(script_path)
            except:
                pass