FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir .

COPY ./api ./api

EXPOSE 8000

CMD ["uvicorn", "api.project:app", "--host", "0.0.0.0", "--port", "8000"]
