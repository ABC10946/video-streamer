FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
	 && apt-get install -y --no-install-recommends \
		 ca-certificates \
		 curl \
		 build-essential \
		 pkg-config \
		 git \
		 libgstreamer1.0-dev \
		 libgstreamer-plugins-base1.0-dev \
		 libgstreamer-plugins-bad1.0-dev \
		 libgstrtspserver-1.0-dev \
		 gstreamer1.0-tools \
		 gstreamer1.0-plugins-base \
		 gstreamer1.0-plugins-good \
		 gstreamer1.0-plugins-bad \
		 gstreamer1.0-plugins-ugly \
		 gstreamer1.0-libav \
		 gstreamer1.0-x \
		 gstreamer1.0-alsa \
		 gstreamer1.0-gl \
		 gstreamer1.0-gtk3 \
		 gstreamer1.0-qt5 \
		 gstreamer1.0-pulseaudio \
		 meson \
		 ninja-build \
	&& rm -rf /var/lib/apt/lists/*

# Download and compile the test-launch example from gst-rtsp-server
RUN git clone --depth 1 https://gitlab.freedesktop.org/gstreamer/gst-rtsp-server.git $HOME/gst-rtsp-server \
    && cd $HOME/gst-rtsp-server \
    && meson build \
    && cd build \
    && ninja \
    && cp examples/test-launch /usr/local/bin/

# default to running test-launch with environment variable expansion
# Use a shell wrapper so $VIDEO_DEVICE and $AUDIO_DEVICE are expanded and
# exec replaces the shell with test-launch (so signals are delivered correctly)
ENV VIDEO_DEVICE=/dev/video0
ENV AUDIO_DEVICE=plughw:1,0
ENV GST_DEBUG=3

# RTSP default port
EXPOSE 8554

# Use /bin/sh -c so environment variables are expanded. exec replaces
# the shell with the test-launch binary so it becomes PID 1.

# cannot work
# CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src do-timestamp=true device=$VIDEO_DEVICE ! video/x-raw,width=640,height=480,framerate=15/1 ! videoconvert ! v4l2h264enc extra-controls=\"controls,video_bitrate=500000\" ! rtph264pay name=pay0 pt=96  alsasrc do-timestamp=true device=$AUDIO_DEVICE ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! avenc_aac ! rtpmp4apay name=pay1 pt=97 )\""]


# cannot work
# CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src device=$VIDEO_DEVICE do-timestamp=true ! video/x-raw,width=640,height=480,framerate=15/1 ! videoconvert ! v4l2h264enc extra-controls=\"controls,video_bitrate=500000\" ! h264parse ! rtph264pay name=pay0 pt=96 aggregate-mode=zero config-interval=1 alsasrc device=$AUDIO_DEVICE do-timestamp=true ! audioconvert ! audioresample ! audio/x-raw,rate=44100,channels=1 ! voaacenc bitrate=64000 ! rtpmp4apay name=pay1 pt=97 )\""]


# cannot work
# CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src device=$VIDEO_DEVICE ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! v4l2h264enc extra-controls=\"controls,video_bitrate=800000\" ! h264parse ! rtph264pay name=pay0 pt=96 )\""]

# it is able to work
# CPU encoding
# CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src device=$VIDEO_DEVICE ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96)\""]

# CPU encoding with audio
CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src device=$VIDEO_DEVICE ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96  alsasrc do-timestamp=true device=$AUDIO_DEVICE ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! avenc_aac ! rtpmp4apay name=pay1 pt=97 )\""]

# hardware encoding
# cannot work
# CMD ["/bin/sh", "-c", "exec /usr/local/bin/test-launch \"( v4l2src device=$VIDEO_DEVICE ! image/jpeg,width=640,height=480,framerate=30/1 ! jpegdec ! videoconvert ! v4l2h264enc ! h264parse ! rtph264pay name=pay0 pt=96 )\""]
