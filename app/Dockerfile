FROM python:3.11-buster

COPY requirements.txt /app/
WORKDIR /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install application
COPY *.py /app/

RUN mkdir {file-type-1, file-type-2}

COPY file-type-1/*.py /app/file-type-1/
COPY file-type-2/*.py /app/file-type-2/

EXPOSE 8000

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "main:app"]