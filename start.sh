#!/bin/bash

tmux has-session -t main 2>/dev/null || tmux new-session -d -s main -n inspect 'inspect view --host 0.0.0.0'
tmux has-session -t main:server 2>/dev/null || tmux new-window -t main -n server 'sudo ./venv/bin/python server.py'
tmux attach-session -t main
