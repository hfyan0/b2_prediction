#!/bin/bash

B2_PREDICTION_CLIENT=/home/$(whoami)/Dropbox/nirvana/b2_prediction/b2_prediction_client.py
CONFIG_LIVE=/home/$(whoami)/Dropbox/nirvana/b2_prediction/config_live_8.ini

python $B2_PREDICTION_CLIENT $CONFIG_LIVE
