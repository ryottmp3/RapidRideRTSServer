#!/bin/bash

# Starts server for Rapid Ride RTS
# MIT License
# Copyright © 2025 H. Ryott Glayzer

echo -e "\033[1;32m Starting Uvicorn Server with debug level TRACE \033[0m"
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level trace
