#!/usr/bin/env python3
"""
Flask-based static file server with HTTP Basic Auth protection for selected paths.

Environment variables:
  BASIC_AUTH_USER (default: admin)
  BASIC_AUTH_PASS (default: password)
  BASIC_AUTH_REALM (default: Restricted)
  AUTH_ALL (if set to 1/true, require auth for all paths)
  PORT (default: 8000)

Serves files from `/app` (the Docker image copies `./streamer` to `/app`).
"""
import os
from functools import wraps
from flask import Flask, request, Response, send_from_directory, abort


USER = os.getenv("BASIC_AUTH_USER", "admin")
PASS = os.getenv("BASIC_AUTH_PASS", "password")
REALM = os.getenv("BASIC_AUTH_REALM", "Restricted")
AUTH_ALL = os.getenv("AUTH_ALL", "0").lower() in ("1", "true", "yes")
PORT = int(os.getenv("PORT", "8000"))

APP_DIR = '/app'

app = Flask(__name__, static_folder=APP_DIR, static_url_path='')


def check_auth():
    auth = request.authorization
    if not auth:
        return False
    return auth.username == USER and auth.password == PASS


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        path = request.path
        protected = AUTH_ALL or path in ('/', '/index.html', '/stream_simple.html')
        if protected and not check_auth():
            return Response('Unauthorized', 401, {'WWW-Authenticate': f'Basic realm="{REALM}"'})
        return f(*args, **kwargs)
    return decorated


@app.route('/', defaults={'filename': 'index.html'})
@app.route('/<path:filename>')
@requires_auth
def serve_file(filename):
    fullpath = os.path.join(APP_DIR, filename)
    if os.path.isdir(fullpath):
        # if directory, try index.html inside it
        index = os.path.join(fullpath, 'index.html')
        if os.path.exists(index):
            return send_from_directory(fullpath, 'index.html')
        abort(404)
    if not os.path.exists(fullpath):
        abort(404)
    return send_from_directory(APP_DIR, filename)


if __name__ == '__main__':
    os.chdir(APP_DIR)
    print(f"Starting Flask server on 0.0.0.0:{PORT} (auth={'ALL' if AUTH_ALL else 'SELECT'})")
    app.run(host='0.0.0.0', port=PORT)
