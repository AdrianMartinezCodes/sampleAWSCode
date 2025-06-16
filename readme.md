# 🛰️ AWS Metadata API

---

## Requirements

- Python 3.12+
- Pip (for dependency management)
- Docker (for containerized deployment)
- (Optional) `pre-commit` for development hooks

---

## Running Locally

Install dependencies:

```bash
pip install -e ".[dev,test]"
```

Start the API:
```bash
uvicorn api.project:app --reload
```

## Run Tests
Just run 
```bash
pytest
```

## Build the Docker

You can build the image with
```bash
docker build -t metadata-api .
```

and run the container
```bash
docker run -p 8000:8000 metadata-api
```