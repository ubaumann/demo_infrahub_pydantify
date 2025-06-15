ARG INFRAHUB_VERSION=latest
FROM registry.opsmill.io/opsmill/infrahub:${INFRAHUB_VERSION}

# Install specific package
WORKDIR /opt/local
COPY . .
RUN pip install -e .

WORKDIR /source