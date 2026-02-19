FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    confluent-kafka \
    pydantic \
    pyyaml

COPY src/generators/ /app/src/generators/
COPY src/models/ /app/src/models/
COPY src/utils/ /app/src/utils/
COPY src/__init__.py /app/src/__init__.py
COPY config/ /app/config/
COPY scripts/generate_events.py /app/generate_events.py

USER nobody

ENTRYPOINT ["python", "generate_events.py"]
