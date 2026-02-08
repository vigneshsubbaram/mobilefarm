FROM python:3.13-slim-bookworm

RUN apt-get update -y && apt install -y git gcc unzip wget && pip install uv && \
    git clone https://github.com/vigneshsubbaram/pytest-mobilefarm.git && \
    cd pytest-mobilefarm && uv pip install . --system && \
    git clone https://github.com/vigneshsubbaram/mobilefarm.git && \
    cd mobilefarm && uv pip install . --system && \
    wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip \
    -O /opt/platform-tools-latest-linux.zip \
    && unzip /opt/platform-tools-latest-linux.zip -d /opt/ && \
    rm /opt/platform-tools-latest-linux.zip

ENV ANDROID_HOME=/opt/platform-tools
ENV PATH="${ANDROID_HOME}:${PATH}"

WORKDIR /workspace

CMD ["/bin/bash"]
