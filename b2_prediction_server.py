import zmq
import random
import time
import sys
import ConfigParser
from datetime import datetime, date
import math
from b2_prediction_common import B2_rpy_prediction

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
ForecastFolderArima  =     config.get("ARIMA"     , "ForecastFolder")
ForecastFolderTaylor =     config.get("Taylor"    , "ForecastFolder")

###################################################
# obj
###################################################
b2_rpy_prediction= B2_rpy_prediction(configfile)

###################################################
# load previous forecasts
###################################################

print "Start loading previous forecasts"
b2_rpy_prediction.load_prev_forecasts()
print "Finished loading previous forecasts"

###################################################
# zmq
###################################################
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:%s" % ServerPort)

while True:
    message = socket.recv()
    msg_csv = message.split(",")
    if len(msg_csv) < 6:
        continue
    dt = datetime.strptime(msg_csv[0],"%Y-%m-%d").date()
    sym = msg_csv[1]
    o = msg_csv[2]
    h = msg_csv[3]
    l = msg_csv[4]
    c = msg_csv[5]
    model = msg_csv[6]

    prev_fcast = b2_rpy_prediction.get_prev_forecast(dt,sym,model)
    if prev_fcast is None:
        sPrevFcast = "-1.0"
    else:
        sPrevFcast = str(prev_fcast)
    print "%s %s %s" % (dt,sym,sPrevFcast)
    socket.send(sPrevFcast)

