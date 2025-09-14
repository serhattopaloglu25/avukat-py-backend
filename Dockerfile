FROM python:3.11-slim

WORKDIR /app

COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]