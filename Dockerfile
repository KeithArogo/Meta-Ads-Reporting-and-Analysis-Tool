FROM python:3.9-slim

WORKDIR /app

# Copy project files
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src ./src
COPY main.py .

ENTRYPOINT ["python", "main.py"]
