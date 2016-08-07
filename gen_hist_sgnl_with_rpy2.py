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
outfile_coef_arima = open(CoefFolderArima+"/"+symbol+".csv", "w")
outfile_fcast_arima = open(ForecastFolderArima+"/"+symbol+".csv", "w")
outfile_coef_taylor = open(CoefFolderTaylor+"/"+symbol+".csv", "w")
outfile_fcast_taylor = open(ForecastFolderTaylor+"/"+symbol+".csv", "w")

###################################################
# loop through historical data
###################################################
for how_many_days_bk in range(1,len(py_ls_date_full)):

    for barintvl in range(1,MaxBarIntervalArima+1):

        for barintvlshift in range(0,barintvl):

            (py_fit_coef, fc_pxreturn_1d) = b2_rpy_prediction.calc_forecast(B2_rpy_prediction.ARIMA, py_ls_date_full, py_ls_ln_avgpx_full, how_many_days_bk, barintvl, barintvlshift)

            if py_fit_coef is None or fc_pxreturn_1d is None:
                continue

            outfile_coef_arima.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_coef_arima.write(",")
            outfile_coef_arima.write(symbol)
            outfile_coef_arima.write(",")
            outfile_coef_arima.write(str(how_many_days_bk))
            outfile_coef_arima.write(",")
            outfile_coef_arima.write(str(barintvl))
            outfile_coef_arima.write(",")
            outfile_coef_arima.write(str(barintvlshift))
            outfile_coef_arima.write(",")
            outfile_coef_arima.write(",".join(map(lambda x: str(x), py_fit_coef)))
            outfile_coef_arima.write("\n")

            outfile_fcast_arima.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_fcast_arima.write(",")
            outfile_fcast_arima.write(symbol)
            outfile_fcast_arima.write(",")
            outfile_fcast_arima.write(str(how_many_days_bk))
            outfile_fcast_arima.write(",")
            outfile_fcast_arima.write(str(barintvl))
            outfile_fcast_arima.write(",")
            outfile_fcast_arima.write(str(barintvlshift))
            outfile_fcast_arima.write(",")
            outfile_fcast_arima.write(str(fc_pxreturn_1d))
            outfile_fcast_arima.write("\n")

            (py_fit_coef, fc_pxreturn_1d) = b2_rpy_prediction.calc_forecast(B2_rpy_prediction.TAYLOR, py_ls_date_full, py_ls_ln_avgpx_full, how_many_days_bk, barintvl, barintvlshift)

            if py_fit_coef is None or fc_pxreturn_1d is None:
                continue

            outfile_coef_taylor.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_coef_taylor.write(",")
            outfile_coef_taylor.write(symbol)
            outfile_coef_taylor.write(",")
            outfile_coef_taylor.write(str(how_many_days_bk))
            outfile_coef_taylor.write(",")
            outfile_coef_taylor.write(str(barintvl))
            outfile_coef_taylor.write(",")
            outfile_coef_taylor.write(str(barintvlshift))
            outfile_coef_taylor.write(",")
            outfile_coef_taylor.write(",".join(map(lambda x: str(x), py_fit_coef)))
            outfile_coef_taylor.write("\n")

            outfile_fcast_taylor.write(str(py_ls_date_full[-how_many_days_bk]))
            outfile_fcast_taylor.write(",")
            outfile_fcast_taylor.write(symbol)
            outfile_fcast_taylor.write(",")
            outfile_fcast_taylor.write(str(how_many_days_bk))
            outfile_fcast_taylor.write(",")
            outfile_fcast_taylor.write(str(barintvl))
            outfile_fcast_taylor.write(",")
            outfile_fcast_taylor.write(str(barintvlshift))
            outfile_fcast_taylor.write(",")
            outfile_fcast_taylor.write(str(fc_pxreturn_1d))
            outfile_fcast_taylor.write("\n")

outfile_coef_arima.close()
outfile_fcast_arima.close()
outfile_coef_taylor.close()
outfile_fcast_taylor.close()
