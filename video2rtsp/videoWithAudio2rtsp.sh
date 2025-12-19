#!/bin/bash
#
VIDEO_DEVICE=${1:-"/dev/video0"}
AUDIO_DEVICE=${2:-"plughw:1,0"}

sudo test-launch "( \
        v4l2src do-timestamp=true device=$VIDEO_DEVICE ! videoconvert ! x264enc tune=zerolatency bitrate=2000 ! rtph264pay name=pay0 pt=96 \
        alsasrc do-timestamp=true device=$AUDIO_DEVICE ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! avenc_aac ! rtpmp4apay name=pay1 pt=97 \
)"
