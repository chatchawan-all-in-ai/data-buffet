# Build context = the directory setup.sh stages: publisher/, sql/diff.sql and a copy of
# includes/controller/mart-export-config.json.
FROM python:3.12-slim
WORKDIR /app
COPY publisher/requirements.txt publisher/requirements.txt
RUN pip install --no-cache-dir -r publisher/requirements.txt
COPY publisher/main.py publisher/main.py
COPY sql/diff.sql sql/diff.sql
COPY config/mart-export-config.json config/mart-export-config.json
ENTRYPOINT ["python", "-u", "publisher/main.py"]
