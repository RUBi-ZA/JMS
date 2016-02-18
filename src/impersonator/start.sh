#!/bin/bash

exec nohup python server.py 8123 >/dev/null 2>&1 &
