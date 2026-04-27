FROM python:3.12-slim

LABEL io.modelcontextprotocol.server.name="io.github.prakhargour10/utility-mcp-server"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

COPY main.py .
COPY utility_mcp_server/ utility_mcp_server/
COPY sdk/ sdk/

EXPOSE 8000

ENTRYPOINT ["python", "main.py"]
