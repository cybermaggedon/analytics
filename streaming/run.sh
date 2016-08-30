#!/bin/bash

setsid wye-service >/dev/null 2>&1 < /dev/null &

python cyber.py

while true
do
  sleep 10000
done
