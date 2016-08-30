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

MaxBarIntervalArima    = int(config.get("ARIMA", "MaxBarInterval"      ))
MaxBarIntervalTaylor   = int(config.get("Taylor", "MaxBarInterval"     ))

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

###################################################
STR_UNDEFINED="-1.0"
while True:
    message = socket.recv()
    print "message received: %s" % (message)
    ###################################################
    # testing
    ###################################################
    if "ping" in message or "test" in message:
        socket.send(STR_UNDEFINED)
        continue
    ###################################################
    msg_csv = message.split(",")
    if len(msg_csv) < 6:
        socket.send(STR_UNDEFINED)
        continue
    dt = datetime.strptime(msg_csv[0],"%Y-%m-%d").date()
    symbol = msg_csv[1]
    o = msg_csv[2]
    h = msg_csv[3]
    l = msg_csv[4]
    c = msg_csv[5]
    v = msg_csv[6]
    model = int(msg_csv[7].rstrip('\0'))

    prev_fcast = b2_rpy_prediction.get_prev_forecast(dt,symbol,model)
    if prev_fcast is None:
        print "Forecast for %s on %s is unavailable." % (symbol,dt)
        sPrevFcast = STR_UNDEFINED

        ###################################################
        # calculate the latest prediction on the fly
        ###################################################
        (py_ls_date_full, py_ls_ln_avgpx_full) = b2_rpy_prediction.get_hist_price_data(symbol)

        if dt <= datetime.strptime(py_ls_date_full[-1],"%Y-%m-%d").date():
            print "But should not calculate prediction"
            socket.send(STR_UNDEFINED)
            continue
        ###################################################
        # append today's OHLC
        ###################################################
        ln_avgpx = math.log((float(h) + float(l) + float(c)) / 3.0)
        py_ls_date_full.append(str(dt))
        py_ls_ln_avgpx_full.append(ln_avgpx)
        ###################################################

        how_many_days_bk = 1

        for barintvl in range(1,MaxBarIntervalArima+1):

            for barintvlshift in range(0,barintvl):

                (py_fit_coef, fc_pxreturn_1d) = b2_rpy_prediction.calc_forecast(model, py_ls_date_full, py_ls_ln_avgpx_full, how_many_days_bk, barintvl, barintvlshift)

                if py_fit_coef is None or fc_pxreturn_1d is None:
                    continue

                print model, symbol, dt, str(barintvl) + "_" + str(barintvlshift), fc_pxreturn_1d
                b2_rpy_prediction.add_forecast(model, symbol, dt, str(barintvl) + "_" + str(barintvlshift), fc_pxreturn_1d)

        prev_fcast = b2_rpy_prediction.get_prev_forecast(dt,symbol,model)
        sPrevFcast = str(prev_fcast)

    else:
        sPrevFcast = str(prev_fcast)
    print "%s %s %s" % (dt,symbol,sPrevFcast)
    socket.send(sPrevFcast)
