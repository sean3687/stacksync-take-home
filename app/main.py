from flask import Flask, request, jsonify
import os
from .executor import CodeExecutor
from .validator import ScriptValidator

app = Flask(__name__)

# Initialize the code executor with the nsjail config path
executor = CodeExecutor(
    config_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nsjail', 'config.proto')
)

@app.route('/execute', methods=['POST'])
def execute_code():
    try:
        data = request.get_json()
        
        # Validate the request
        is_valid, error_message = ScriptValidator.validate_request(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400

        script = data['script']
        
        # Execute the script in the secure environment
        result = executor.execute(script)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080) 