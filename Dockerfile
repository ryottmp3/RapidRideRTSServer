FROM python:3.13-slim

# Set Working Directory
WORKDIR /app

# Copy Files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI port
Expose 8080

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8080"]
