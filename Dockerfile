# Generated by https://smithery.ai. See: https://smithery.ai/docs/config#dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy necessary project files
COPY pyproject.toml ./
COPY README.md ./
COPY src/ ./src/

# Upgrade pip and install build dependencies
RUN pip install --upgrade pip \
    && pip install hatchling

# Install the package (skip prepare scripts if any)
RUN pip install --ignore-installed --no-cache-dir .

# MCP server runs over stdio so no ports are exposed

# Start the MCP server using the entrypoint installed by setup
CMD ["mysqldb-mcp-server"]
