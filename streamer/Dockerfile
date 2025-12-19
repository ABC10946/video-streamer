FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        python3 \
    && rm -rf /var/lib/apt/lists/*

COPY ./streamer /app/

WORKDIR /app/

# start.sh will run streamer.sh (background) and python http.server (foreground)
COPY ./streamer/start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]