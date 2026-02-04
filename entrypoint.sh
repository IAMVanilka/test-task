#!/bin/sh
python init_app.py
exec python main.py --host 0.0.0.0 --port 8000