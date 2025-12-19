#!/bin/bash

# Start Backend in background
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &

# Start Frontend in foreground
streamlit run frontend/app.py --server.port 8080 --server.address 0.0.0.0
