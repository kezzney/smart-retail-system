FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libsm6 \
    libice6 \
    libfontconfig1 \
    libfreetype6 \
    ca-certificates \
    curl \
    && ldconfig \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/backend/

ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Explicitly expose the standard Debian library locations
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib:/lib/x86_64-linux-gnu:/lib

# Fail-fast verification: verify native libraries AND cv2 during image build
RUN echo "=== OS ===" \
    && cat /etc/os-release \
    && echo "=== Python ===" \
    && python --version \
    && echo "=== libxcb ===" \
    && find /usr /lib -name 'libxcb.so.1*' 2>/dev/null \
    && echo "=== ldconfig libxcb ===" \
    && ldconfig -p | grep libxcb \
    && echo "=== OpenCV ===" \
    && python -c "import cv2; print('cv2 version:', cv2.__version__); print('cv2 path:', cv2.__file__)"

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
