ffmpeg -rtsp_transport tcp -i rtsp://video2rtsp:8554/test \
  -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: \
  text='%{localtime\\:%Y-%m-%d %H\\\\\\:%M\\\\\\:%S}': x=10: y=10: fontsize=24: fontcolor=white: \
  box=1: boxcolor=black@0.5, format=yuv420p" \
  -c:v libx264 -preset ultrafast -tune zerolatency -profile:v main \
  -c:a aac -ar 48000 -b:a 128k \
  -f hls -hls_time 2 -hls_list_size 3 -hls_flags delete_segments stream.m3u8
