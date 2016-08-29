import sys
import ConfigParser
from datetime import datetime, date
import math
import zmq
import time

if len(sys.argv) == 1:
    print "Usage: python ... [config.ini]"
    sys.exit(0)

configfile = sys.argv[1]

###################################################
# config
###################################################
config = ConfigParser.ConfigParser()
config.read(configfile)

ServerPort           = int(config.get("Prediction", "ServerPort" ))
PriceFolder          =     config.get("Prediction", "PriceFolder")

###################################################
# zmq
###################################################
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://127.0.0.1:%s" % ServerPort)

while True:
    ###################################################
    # ARIMA = 1
    # TAYLOR = 2
    ###################################################
    # socket.send('2016-08-26,AGG,112.69,112.8572,112.28,112.34,2513744.0,1')
    # socket.send('2016-08-18,AGG,112.64,112.7799,112.535,112.73,1963011.0,2')
    # socket.send('2016-08-05,AGG,112.54,112.54,112.135,112.17,2474608.0,2')
    socket.send('2016-08-04,AGG,112.54,112.66,112.5,112.55,2002838.0,2')
    # socket.send('2047-12-31,AGG,112.54,112.66,112.5,112.55,2002838.0,2')
    # socket.send('for testing')
    print socket.recv()
    time.sleep(2)
