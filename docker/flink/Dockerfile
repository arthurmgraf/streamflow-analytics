FROM flink:1.20-java17

USER root

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-dev && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    apache-flink==1.20.0 \
    confluent-kafka \
    scikit-learn \
    joblib \
    pydantic \
    pyyaml

COPY src/flink_jobs/ /opt/flink/usrlib/src/flink_jobs/
COPY src/models/ /opt/flink/usrlib/src/models/
COPY src/utils/ /opt/flink/usrlib/src/utils/
COPY src/__init__.py /opt/flink/usrlib/src/__init__.py
COPY config/ /opt/flink/usrlib/config/

RUN chown -R flink:flink /opt/flink/usrlib/
USER flink

WORKDIR /opt/flink
