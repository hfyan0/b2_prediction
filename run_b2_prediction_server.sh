#!/bin/bash

B2_ARIMA_SERVER=/home/qy/Dropbox/nirvana/b2_prediction/b2_prediction_server.py
CONFIG_LIVE=/home/qy/Dropbox/nirvana/b2_prediction/config_live.ini

python $B2_ARIMA_SERVER $CONFIG_LIVE
