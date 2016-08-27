#!/bin/bash

CONFIG_INI=$1
SYMBOLLIST=$(cat $CONFIG_INI|grep -v ^#|grep SymbolList|awk -F= '{print $2}'|tr ',' ' ')
SYMBOLS_FOLDER=$(cat $CONFIG_INI|grep -v ^#|grep SymbolsFolder|awk -F= '{print $2}')

[[ ! -d $SYMBOLS_FOLDER ]] && mkdir -p $SYMBOLS_FOLDER

rm -f $SYMBOLS_FOLDER/*

for sym in $SYMBOLLIST
do
    touch $SYMBOLS_FOLDER/$sym
done
