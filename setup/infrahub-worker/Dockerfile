ARG INFRAHUB_VERSION=latest
FROM registry.opsmill.io/opsmill/infrahub:${INFRAHUB_VERSION}

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt