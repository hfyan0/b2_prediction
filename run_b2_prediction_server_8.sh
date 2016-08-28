#!/bin/bash

B2_PREDICTION_SERVER=/home/$(whoami)/Dropbox/nirvana/b2_prediction/b2_prediction_server.py
CONFIG_LIVE=/home/$(whoami)/Dropbox/nirvana/b2_prediction/config_live_8.ini

python $B2_PREDICTION_SERVER $CONFIG_LIVE
