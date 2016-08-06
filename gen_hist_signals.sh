#!/bin/bash

CONFIG_HIST=/home/qy/Dropbox/nirvana/b2_prediction/config_hist.ini
SYMBOLS_FOLDER=$(ls|grep config|grep ini|head -n 1|xargs cat|grep SymbolsFolder|awk -F= '{print $2}')
GEN_HIST_SGNL_WITH_RPY=/home/qy/Dropbox/nirvana/b2_prediction/gen_hist_sgnl_with_rpy2.py
POPULATE_SYM_SCT=/home/qy/Dropbox/nirvana/b2_prediction/populate_sym_folder.sh

source $POPULATE_SYM_SCT

date
cd $SYMBOLS_FOLDER
ls | time parallel -j+0 --progress --eta python $GEN_HIST_SGNL_WITH_RPY $CONFIG_HIST
date

