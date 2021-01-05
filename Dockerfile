FROM alpine:3.12 AS builder
LABEL maintainer="knthmn@outlook.com"
ARG RCLONE_VERSION=v1.53.3
ARG BORGMATIC_VERSION=1.5.12
RUN apk add \
    py3-pip \
    && pip3 install borgmatic==${BORGMATIC_VERSION} \
    && cd /tmp \
    && wget -q https://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip \
    && unzip -q rclone*.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin \
    && chmod 755 /usr/bin/rclone

FROM alpine:3.12
LABEL maintainer="knthmn@outlook.com"
RUN apk add --no-cache \
    borgbackup \
    tzdata
COPY --from=builder /usr/lib/python3.8/site-packages /usr/lib/python3.8/
COPY --from=builder \ 
    /usr/bin/borgmatic \
    /usr/bin/rclone \
    /usr/bin/
COPY entry.py script.py /

ENV BORG_CACHE_DIR=/mnt/borg_cache
ENV BORG_CONFIG_DIR=/mnt/borg_config
VOLUME [ "/mnt/source", "/mnt/repo", "/mnt/rclone_config", "/mnt/borgmatic", "/mnt/borg_cache", "/mnt/borg_config" ]

ENTRYPOINT ["/usr/bin/python3", "-u", "/entry.py"]