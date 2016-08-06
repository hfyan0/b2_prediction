import sys
import ConfigParser
from datetime import datetime
import math
from b2_prediction_common import B2_rpy_prediction

if len(sys.argv) == 1:
    print "Usage: python ... [config.ini] [symbol]"
    sys.exit(0)

configfile = sys.argv[1]
symbol = sys.argv[2]
print symbol

###################################################
# config
###################################################
config = ConfigParser.ConfigParser()
config.read(configfile)

MaxBarIntervalArima  = int(config.get("ARIMA", "MaxBarInterval"))
CoefFolderArima      =     config.get("ARIMA", "CoefFolder"    )
ForecastFolderArima  =     config.get("ARIMA", "ForecastFolder")

MaxBarIntervalTaylor = int(config.get("Taylor", "MaxBarInterval"))
CoefFolderTaylor     =     config.get("Taylor", "CoefFolder"    )
ForecastFolderTaylor =     config.get("Taylor", "ForecastFolder")

###################################################
# obj
###################################################
b2_rpy_prediction = B2_rpy_prediction(configfile)

###################################################
# get historical price data
###################################################
(py_ls_date_full, py_ls_ln_avgpx_full) = b2_rpy_prediction.get_hist_price_data(symbol)

###################################################
outfile_coef = open(CoefFolderArima+"/"+symbol+".csv", "w")
outfile_fcast = open(ForecastFolderArima+"/"+symbol+".csv", "w")

###################################################
# loop through historical data
###################################################
for how_many_days_bk in range(1,len(py_ls_date_full)):

    for barintvl in range(1,MaxBarIntervalArima+1):

        for barintvlshift in range(0,barintvl):

            (py_fit_coef, fc_pxreturn_1d) = b2_rpy_prediction.calc_forecast(B2_rpy_prediction.ARIMA, py_ls_date_full, py_ls_ln_avgpx_full, how_many_days_bk, barintvl, barintvlshift)

            if py_fit_coef is None or fc_pxreturn_1d is None:
                continue

            outfile_coef.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_coef.write(",")
            outfile_coef.write(symbol)
            outfile_coef.write(",")
            outfile_coef.write(str(how_many_days_bk))
            outfile_coef.write(",")
            outfile_coef.write(str(barintvl))
            outfile_coef.write(",")
            outfile_coef.write(str(barintvlshift))
            outfile_coef.write(",")
            outfile_coef.write(",".join(map(lambda x: str(x), py_fit_coef)))
            outfile_coef.write("\n")

            outfile_fcast.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_fcast.write(",")
            outfile_fcast.write(symbol)
            outfile_fcast.write(",")
            outfile_fcast.write(str(how_many_days_bk))
            outfile_fcast.write(",")
            outfile_fcast.write(str(barintvl))
            outfile_fcast.write(",")
            outfile_fcast.write(str(barintvlshift))
            outfile_fcast.write(",")
            outfile_fcast.write(str(fc_pxreturn_1d))
            outfile_fcast.write("\n")


outfile_coef.close()
outfile_fcast.close()
