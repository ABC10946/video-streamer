FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        tzdata \
        python3 \
        python3-pip \
        python3-flask \
    && rm -rf /var/lib/apt/lists/*

# Set container timezone to JST
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone


COPY ./streamer /app/

WORKDIR /app/

# start.sh will run streamer.sh (background) and python http.server (foreground)
COPY ./streamer/start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/bin/bash", "/app/start.sh"]