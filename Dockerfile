FROM alpine:3.14 AS builder
LABEL maintainer="knthmn@outlook.com"
ARG RCLONE_VERSION=v1.53.3
ARG BORG_VERSION=1.1.17
ARG BORGMATIC_VERSION=1.5.18
RUN apk add \
        py3-pip \
        python3-dev \
        openssl-dev\
        acl-dev \
        linux-headers \
        fuse-dev \
        attr-dev \
        gcc \
        alpine-sdk \
        py3-wheel \
    && pip3 install \
        borgbackup==${BORG_VERSION} \
        borgmatic==${BORGMATIC_VERSION} \
    && cd /tmp \
        && wget -q https://downloads.rclone.org/${RCLONE_VERSION}/rclone-${RCLONE_VERSION}-linux-amd64.zip \
        && unzip -q rclone*.zip \
        && cd rclone-*-linux-amd64 \
        && cp rclone /usr/bin \
        && chmod 755 /usr/bin/rclone

FROM alpine:3.14
LABEL maintainer="knthmn@outlook.com"
RUN apk add --no-cache \
        tzdata \
        python3 \
        openssl \
        libcrypto1.1 \
        libacl \
        musl \
        lz4-libs \
        zstd-libs \
        ca-certificates
COPY --from=builder /usr/lib/python3.9/site-packages /usr/lib/python3.9/
COPY --from=builder \ 
    /usr/bin/borg \
    /usr/bin/borgfs \
    /usr/bin/borgmatic \
    /usr/bin/generate-borgmatic-config  \
    /usr/bin/upgrade-borgmatic-config  \
    /usr/bin/validate-borgmatic-config \
    /usr/bin/rclone \
    /usr/bin/ 
COPY entry.py script.py /
RUN chmod 755 /entry.py /script.py \
    && ln -s /mnt/borgmatic /etc/borgmatic.d \
    && ln -s /mnt/rclone_config/rclone.conf /usr/bin

ENV BORG_CACHE_DIR=/mnt/borg_cache
ENV BORG_CONFIG_DIR=/mnt/borg_config
VOLUME [ "/mnt/source", "/mnt/repo", "/mnt/rclone_config", "/mnt/borgmatic", "/mnt/borg_cache", "/mnt/borg_config" ]

ENTRYPOINT ["/usr/bin/python3", "-u", "/entry.py"]