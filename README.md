# Python Code Execution API

A secure API service that executes Python code in a sandboxed environment.

## Prerequisites

- Docker Desktop
- Python 3.11 or higher (for local development)

## Building and Running

1. Build the Docker image:
```bash
docker build -t python-execution-api .
```

2. Run the container:
```bash
docker run -p 8080:8080 python-execution-api
```

## API Usage

Send a POST request to `/execute` with a JSON body containing the Python script:

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "script": "def main():\n    print(\"Hello, World!\")\n    return 42"
  }'
```

The response will be in the following format:
```json
{
  "result": 42,
  "stdout": "Hello, World!\n"
}
```

## Development

For local development without Docker:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/main.py
```

## Security Notes

- The current implementation is a basic version without nsjail integration
- Do not use this in production without proper security measures
- Additional security features will be added in future updates 