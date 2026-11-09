# Build context = the directory setup.sh stages: publisher/ and sql/diff.sql.
FROM python:3.12-slim
WORKDIR /app
COPY publisher/requirements.txt publisher/requirements.txt
RUN pip install --no-cache-dir -r publisher/requirements.txt
COPY publisher/main.py publisher/main.py
COPY sql/diff.sql sql/diff.sql
ENTRYPOINT ["python", "-u", "publisher/main.py"]
