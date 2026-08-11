# Menggunakan image resmi Microsoft Playwright Python yang sudah menyertakan Chromium & OS dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY . .

# Jalankan script dalam mode daemon
CMD ["python", "main.py", "--daemon"]
