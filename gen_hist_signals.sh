#!/bin/bash

CONFIG_HIST=/home/$(whoami)/Dropbox/nirvana/b2_prediction/config_hist.ini
# CONFIG_HIST=/home/$(whoami)/Dropbox/nirvana/b2_prediction/config_test.ini
SYMBOLS_FOLDER=$(cat $CONFIG_HIST |grep -v ^#|grep SymbolsFolder|awk -F= '{print $2}')
GEN_HIST_SGNL_WITH_RPY=/home/$(whoami)/Dropbox/nirvana/b2_prediction/gen_hist_sgnl_with_rpy2.py
POPULATE_SYM_SCT=/home/$(whoami)/Dropbox/nirvana/b2_prediction/populate_sym_folder.sh

source $POPULATE_SYM_SCT $CONFIG_HIST

###################################################
# create output folders if they don't already exist
###################################################
cat $CONFIG_HIST |grep -v ^#|grep CoefFolder|awk -F= '{print $2}'|xargs mkdir -p
cat $CONFIG_HIST |grep -v ^#|grep ForecastFolder|awk -F= '{print $2}'|xargs mkdir -p

date
cd $SYMBOLS_FOLDER
ls | time parallel -j+0 --progress --eta python $GEN_HIST_SGNL_WITH_RPY $CONFIG_HIST
# python $GEN_HIST_SGNL_WITH_RPY $CONFIG_HIST AGG
date
