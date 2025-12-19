# video-with-audio-streamer

軽量なコンテナ構成で、ホストのカメラ（/dev/video*）とマイク（ALSA）をRTSPで配信する `video2rtsp` サービスと、
そのRTSPを受けて FFmpeg で HLS に変換し、Flask ベースのHTTPサーバで配信する `streamer` サービスを提供するサンプルプロジェクトです。

目次
- 概要
- 構成ファイルと主要スクリプト
- 必要条件
- ビルドと起動（docker-compose）
- 環境変数
- 使い方（確認・アクセス方法）
- /dev/video0 を使う方法
- トラブルシューティング
- セキュリティと運用上の注意

---

## 概要

- `video2rtsp` : GStreamer (`gst-rtsp-server` の `test-launch`) を使い、ホストのカメラ/オーディオを RTSP サーバとして公開します（デフォルト: `rtsp://video2rtsp:8554/test`）。
- `streamer` : RTSP を受けて FFmpeg で HLS を生成し、生成した HLS ファイルと UI を Flask で配信します。`streamer` では Basic 認証が可能です。

プロジェクトはローカル検証や小規模な利用を想定したサンプルであり、本番デプロイ前に設定・セキュリティを見直してください。

## 構成ファイルと主要スクリプト

- `docker-compose.yaml` : サービス定義（`video2rtsp`, `streamer`）
- `video2rtsp/Dockerfile` : gst-rtsp-server のビルド / test-launch の起動設定
- `video2rtsp/videoWithAudio2rtsp.sh` : (必要に応じた) 代替の起動スクリプト
- `streamer/Dockerfile` : FFmpeg と Flask を使う `streamer` イメージ定義
- `streamer/streamer.sh` : FFmpeg を使って RTSP → HLS に変換するスクリプト
- `streamer/start.sh` : コンテナ起動時に `streamer.sh` と Flask サーバを正しく起動・監視するラッパー
- `streamer/main.py` : Flask アプリ（Basic 認証をサポート）
- `streamer/index.html`, `streamer/stream_simple.html` : 配信用 UI

---

## 必要条件

- Docker と docker-compose（バージョンはお使いの環境に合わせてください）
- コンテナからホストのデバイスにアクセスする場合、ホスト側に適切なデバイス（例: `/dev/video0`）とパーミッションが必要です。

---

## ビルドと起動（推奨: docker-compose）

1. プロジェクトルートでビルドと起動:

```bash
docker compose up --build -d
```

2. サービス状態確認:

```bash
docker compose ps
docker compose logs -f streamer
```

個別にビルド・起動する場合（例: `streamer` のみ）:

```bash

docker compose build streamer
docker compose up -d streamer
```

または手動でビルドして実行:

```bash
docker build -t my-streamer -f streamer/Dockerfile /home/abc/Programs/video-with-audio-streamer
docker run --rm -p 8000:8000 -e BASIC_AUTH_USER=myuser -e BASIC_AUTH_PASS=secretpass my-streamer
```

## videoデバイス/オーディオデバイスの検出

/dev/video0やplughw:1,0などのデバイス名はv4ls-ctlやarecordというCLIツールで取得する。

```
$ v4l2-ctl --list-devices
videoデバイスの一覧

$ sudo arecord -l
オーディオデバイスの一覧
```

---

## 環境変数

video2rtsp サービス（`docker-compose.yaml` か `docker run -e` で設定）
- `VIDEO_DEVICE` (デフォルト `/dev/video0`)
- `AUDIO_DEVICE` (例: `plughw:1,0`)

streamer サービス
- `BASIC_AUTH_USER`（デフォルト: `admin`）
- `BASIC_AUTH_PASS`（デフォルト: `password`）
- `BASIC_AUTH_REALM`（デフォルト: `Restricted`）
- `AUTH_ALL`（`1` / `true` をセットすると全パスに対して認証を要求）
- `PORT`（デフォルト: `8000`）

例: `docker run -e BASIC_AUTH_USER=alice -e BASIC_AUTH_PASS=xxx -p 8000:8000 my-streamer`

---

## 使い方（アクセス方法）

- RTSP（内部サービス名）: `rtsp://video2rtsp:8554/test`（docker-compose ネットワーク内で利用）
- HTTP (HLS / UI): `http://<ホスト>:8000/`（Flask が配信）
  - `index.html` と `stream_simple.html` があり、Basic 認証で保護されています（設定したユーザ/パスワードを使用）。

HLS 再生の簡単な確認:
- ブラウザで `http://<HOST>:8000/stream_simple.html` を開く（認証ダイアログが出る）
- または VLC などで `http://<HOST>:8000/stream.m3u8` を開く

---

## /dev/video0 をコンテナで使う方法

安全にデバイスを渡す方法:

```yaml
services:
  video2rtsp:
    build:
      context: .
      dockerfile: video2rtsp/Dockerfile
    devices:
      - /dev/video0:/dev/video0
    environment:
      - VIDEO_DEVICE=/dev/video0
      - AUDIO_DEVICE=plughw:1,0
    ports:
      - "8554:8554"
    restart: unless-stopped

# 注意: docker-compose の `privileged: true` は強力な権限を与えるため、最小権限で動かせるなら devices 指定だけにしてください。
```

デバイスが見えない・権限エラーが出る場合:
- ホストで `/dev/video0` の所有者・パーミッションを確認
- 他プロセスがデバイスを占有していないか確認
- 必要なら一時的に `--privileged` を付けてデバッグ（本番では避ける）

---

## トラブルシューティング

- ビルド時に Flask の pip インストールでエラー (PEP 668):
  - 対処済み: `streamer/Dockerfile` は `python3-flask` を apt で入れるように変更しました。

- `RTSP に接続できない`:
  - `video2rtsp` コンテナのログを確認: `docker compose logs video2rtsp`
  - `test-launch` のパイプラインが正しいか（`VIDEO_DEVICE` / `AUDIO_DEVICE`）を確認

- `HLS が更新されない`:
  - `streamer/streamer.sh` の FFmpeg コマンドが RTSP に接続できているか確認
  - HLS 出力ディレクトリ（`/app/hls` 等）に `.m3u8` と `.ts` ファイルが生成されているか確認

- `認証で弾かれる`:
  - 環境変数 `BASIC_AUTH_USER` / `BASIC_AUTH_PASS` が正しく渡されているかを確認
  - `docker compose logs streamer` で Flask の起動メッセージを確認

---

## セキュリティと運用上の注意

- デフォルトの `admin:password` は開発用です。本番では必ず強力なパスワードを環境変数で設定してください。
- Basic 認証は平文認証情報をベースにするため、TLS（HTTPS）を組み合わせることを推奨します。簡単にはリバースプロキシ（nginx）で TLS 終端を行う方法が一般的です。
- コンテナにホストデバイスを直接渡す場合は権限に注意してください。可能な限り最小権限で運用してください。

---

## 開発・拡張の提案

- Flask を本番用にする場合は `gunicorn`、`nginx` などで運用する
- HLS の細かい設定（segment length, playlist length, hls_flags）を環境変数で可変化する
- 認証を OAuth2/OpenID Connect 等に置き換える

---

もし README に追加したいスクリーンショット、例コマンド、あるいはデプロイ手順（systemd / Kubernetes）などの希望があれば教えてください。

