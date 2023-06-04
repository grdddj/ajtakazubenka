#!/bin/sh

cd "$(dirname "$0")"

./status.sh

python_pid=$(ps -ef | grep uvicorn | grep -v grep | grep 4321 | awk '{print $2}')
echo "Killing - PID $python_pid"
kill -9 $python_pid
echo "Starting again"
nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 4321 &

./status.sh
