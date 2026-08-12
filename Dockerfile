# Menggunakan image resmi Microsoft Playwright Python yang sudah menyertakan Chromium & OS dependencies
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Set working directory
WORKDIR /app

# Install Node.js untuk build React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Copy requirements dan install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

# Copy seluruh source code
COPY . .

# Build React frontend
RUN npm run build

# Expose port (Render menetapkan $PORT secara otomatis)
EXPOSE 10000

# Jalankan script dalam mode daemon 24/7
CMD ["python", "main.py", "--daemon"]
