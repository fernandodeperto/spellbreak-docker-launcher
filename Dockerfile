FROM brendoncintas/spellbreak_game_server

ARG S6_OVERLAY_VERSION=3.2.1.0
RUN apt-get update && apt-get install xz-utils
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz

COPY s6/server /etc/s6-overlay/s6-rc.d/server
COPY s6/update /etc/s6-overlay/s6-rc.d/update
COPY scripts /etc/s6-overlay/scripts

RUN touch /etc/s6-overlay/s6-rc.d/user/contents.d/server && \
    touch /etc/s6-overlay/s6-rc.d/user/contents.d/update && \
    mkdir -p /etc/s6-overlay/s6-rc.d/server/dependencies.d && \
    mkdir -p /etc/s6-overlay/s6-rc.d/update/dependencies.d && \
    touch /etc/s6-overlay/s6-rc.d/server/dependencies.d/base && \
    touch /etc/s6-overlay/s6-rc.d/update/dependencies.d/base && \
    touch /etc/s6-overlay/s6-rc.d/server/dependencies.d/update

WORKDIR /spellbreak-server/spellbreak-server
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["/init"]
