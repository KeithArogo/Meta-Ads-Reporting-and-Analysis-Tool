FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src ./src
COPY data ./data
COPY scripts ./scripts
COPY reports ./reports
COPY main.py .

ENTRYPOINT ["python", "main.py"]
