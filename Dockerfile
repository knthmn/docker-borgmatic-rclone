FROM alpine:latest as builder
LABEL maintainer="knthmn@outlook.com"
RUN apk upgrade \
    && apk add \
    alpine-sdk \
    python3-dev \
    py3-pip \
    openssl-dev \
    lz4-dev \
    acl-dev \
    linux-headers \
    fuse-dev \
    attr-dev \
    && pip3 install --upgrade pip \
    && pip3 install --upgrade borgbackup borgmatic \
    && cd /tmp \
    && wget -q https://downloads.rclone.org/rclone-current-linux-amd64.zip \
    && unzip -q rclone*.zip \
    && cd rclone-*-linux-amd64 \
    && cp rclone /usr/bin \
    && chmod 755 /usr/bin/rclone

FROM alpine:latest
LABEL maintainer="knthmn@outlook.com"
RUN apk upgrade \
    && apk add \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    tzdata \
    sshfs \
    python3 \
    openssl \
    fuse \
    ca-certificates \
    lz4-libs \
    libacl \
    msmtp \
    postgresql-client \
    busybox-suid \
    && ln -sf /usr/bin/msmtp /usr/sbin/sendmail \
    && rm -rf /var/cache/apk/*
COPY --from=builder /usr/lib/python3.8/site-packages /usr/lib/python3.8/
COPY --from=builder \ 
    /usr/bin/borg \
    /usr/bin/borgfs \
    /usr/bin/borgmatic \
    /usr/bin/generate-borgmatic-config \
    /usr/bin/upgrade-borgmatic-config \
    /usr/bin/rclone \
    /usr/bin/

COPY entry.py /entry.py
COPY script.py /script.py

ENV BORG_CACHE_DIR=/mnt/borg_cache
ENV BORG_CONFIG_DIR=/mnt/borg_config
VOLUME [ "/mnt/source", "/mnt/repo", "/mnt/rclone_config", "/mnt/borgmatic", "/mnt/borg_cache", "/mnt/borg_config" ]

ENTRYPOINT ["/usr/bin/python3", "-u", "/entry.py"]