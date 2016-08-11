#!/bin/bash

SYMBOLLIST=$(ls|grep config|grep ini|head -n 1|xargs cat|grep -v ^#|grep SymbolList|awk -F= '{print $2}'|tr ',' ' ')
SYMBOLS_FOLDER=$(ls|grep config|grep ini|head -n 1|xargs cat|grep -v ^#|grep SymbolsFolder|awk -F= '{print $2}')

[[ ! -d $SYMBOLS_FOLDER ]] && mkdir -p $SYMBOLS_FOLDER

for sym in $SYMBOLLIST
do
    touch $SYMBOLS_FOLDER/$sym
done

rm -f $SYMBOLS_FOLDER/*core*
