#!/bin/bash

ps aux| grep python | grep -e rpy -e b2_arima | awk '{print $2}' | xargs kill
