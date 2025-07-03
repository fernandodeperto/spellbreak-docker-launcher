FROM brendoncintas/spellbreak_game_server

ARG S6_OVERLAY_VERSION=3.2.1.0
RUN apt-get update && apt-get install xz-utils
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-x86_64.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-x86_64.tar.xz
ENTRYPOINT ["/init"]

WORKDIR /spellbreak-server/spellbreak-server
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "-m", "server.server"]
