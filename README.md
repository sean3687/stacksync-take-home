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

## Security Notes

- The current implementation is a basic version without nsjail integration
- Do not use this in production without proper security measures
- Additional security features will be added in future updates 
