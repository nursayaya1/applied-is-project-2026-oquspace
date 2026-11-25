"""Community Cloud entrypoint. Docker remains the main deployment method."""
import os
import runpy
import sys
import threading
import time
import urllib.request

import streamlit as st
import uvicorn


@st.cache_resource
def start_backend():
    from app.main import app
    config = uvicorn.Config(app, host='127.0.0.1', port=8011, log_level='warning')
    server = uvicorn.Server(config)
    worker = threading.Thread(target=server.run, daemon=True)
    worker.start()
    for _ in range(100):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8011/', timeout=1):
                return server
        except OSError:
            time.sleep(.1)
    raise RuntimeError('Backend не запустился')


if not os.getenv('BACKEND_URL'):
    start_backend()
    os.environ['BACKEND_URL'] = 'http://127.0.0.1:8011'
runpy.run_path('app/frontend/ui.py', run_name='__main__')
