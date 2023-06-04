#!/bin/sh

cd "$(dirname "$0")"

ps -ef | grep uvicorn | grep -v grep | grep 4321
