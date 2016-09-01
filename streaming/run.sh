#!/bin/bash

setsid wye-service &

sleep 1

python cyber.py

while true
do
  sleep 10000
done

