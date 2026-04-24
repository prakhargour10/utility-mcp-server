FROM python:3.12-slim

LABEL io.modelcontextprotocol.server.name="io.github.prakhargour10/utility-mcp-server"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

COPY main.py .
COPY api-docs/ api-docs/

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
