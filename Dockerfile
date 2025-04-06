FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "dashboard.py"]

LABEL org.opencontainers.image.source=https://github.com/EricH9958/Soularr-Dashboard
LABEL org.opencontainers.image.description="Soularr Dashboard - A web interface for Soularr logs and failure lists"
LABEL org.opencontainers.image.licenses=MIT
