ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]
ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_ROOT_USER_ACTION=ignore

# Install Python runtime and dependencies
RUN apk add --no-cache python3 py3-pip \
    && mkdir -p /app

# Install requirements
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Copy application
COPY app.py /app/app.py
EXPOSE 8099
CMD ["python3", "-u", "/app/app.py"]
