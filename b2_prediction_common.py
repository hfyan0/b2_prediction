import sys
import ConfigParser
from datetime import datetime
from rpy2.robjects.packages import importr
import rpy2.robjects as R
import math
from os import listdir
from os.path import isfile, join

class B2_rpy_prediction(object):
    ARIMA  = 1
    TAYLOR = 2

    def __init__(self, configfile):
        R.r('library(tseries)')
        R.r('library(forecast)')

        config = ConfigParser.ConfigParser()
        config.read(configfile)

        self.PriceFolder          =     config.get("Prediction", "PriceFolder")
        self.TrainingPeriodArima  = int(config.get("ARIMA"     , "TrainingPeriod"))
        self.TrainingPeriodTaylor = int(config.get("Taylor"    , "TrainingPeriod"))
        
        self.prev_forecasts = {}

    def get_hist_price_data(self, symbol):
        py_ls_date_full = []
        py_ls_ln_avgpx_full = []
        with open(self.PriceFolder+'/'+symbol+'.csv','r') as f:
            for line in f:
                csv = line.strip().split(",")
                if len(csv) < 6:
                    continue
                py_ls_date_full.append(csv[0])
                ln_avgpx = math.log((float(csv[3]) + float(csv[4]) + float(csv[5])) / 3.0)
                py_ls_ln_avgpx_full.append(ln_avgpx)
        return (py_ls_date_full, py_ls_ln_avgpx_full)

    def load_prev_forecasts(self, fcast_folder):
        filelist = [ f for f in listdir(fcast_folder) if isfile(join(fcast_folder,f)) ]
        # print filelist
        for symfile in filelist:
            ###################################################
            # FIXME: right now there will be no result if it wasn't already in the file
            ###################################################
            with open(fcast_folder+'/'+symfile,'r') as f:
                for line in f:
                    csv = line.strip().split(",")
                    if len(csv) < 6:
                        continue

                    dt = datetime.strptime(csv[0],"%Y-%m-%d").date()
                    sym = csv[1]
                    barintvl_shift = csv[3]+'_'+csv[4]
                    fcast = float(csv[5])

                    if sym not in self.prev_forecasts:
                        self.prev_forecasts[sym] = {}

                    if dt not in self.prev_forecasts[sym]:
                        self.prev_forecasts[sym][dt] = {}

                    self.prev_forecasts[sym][dt][barintvl_shift] = fcast
        # print self.prev_forecasts

    def get_prev_forecast(self, dt, sym):
        agg_fcast = 0.0

        if sym not in self.prev_forecasts:
            return None
        if dt not in self.prev_forecasts[sym]:
            return None

        barintvl_cnt = []
        barintvl_tot1drtn = []

        for barintvl in range(50):
            barintvl_cnt.append(0)
            barintvl_tot1drtn.append(0)

        for k,v in self.prev_forecasts[sym][dt].iteritems():
            ls_k = map(lambda x: int(x), k.split("_"))
            barintvl = ls_k[0]
            barintvl_shift = ls_k[1]
            fcast = v
            barintvl_cnt[barintvl] += 1
            barintvl_tot1drtn[barintvl] += fcast

        tot_barintvl_present = len(filter(lambda x: x > 0, barintvl_cnt))

        for barintvl in range(50):
            if barintvl_cnt[barintvl] > 0:
                agg_fcast += barintvl_tot1drtn[barintvl] / barintvl_cnt[barintvl] / tot_barintvl_present

        return agg_fcast

    def calc_forecast(self, model, py_ls_date_full, py_ls_ln_avgpx_full, how_many_days_bk, barintvl, barintvlshift):

        py_ls_date_tmp = py_ls_date_full[barintvlshift:-how_many_days_bk]
        py_ls_ln_avgpx_tmp = py_ls_ln_avgpx_full[barintvlshift:-how_many_days_bk]

        py_ls_date = []
        py_ls_ln_avgpx = []

        iCnt=0
        for d in py_ls_date_tmp:
            if iCnt % barintvl == 0:
                py_ls_date.append(d)
            iCnt += 1

        iCnt=0
        for p in py_ls_ln_avgpx_tmp:
            if iCnt % barintvl == 0:
                py_ls_ln_avgpx.append(p)
            iCnt += 1

        if model == B2_rpy_prediction.ARIMA:
            trainingPeriod = self.TrainingPeriodArima
        elif model == self.TAYLOR:
            trainingPeriod = self.TrainingPeriodTaylor

        if len(py_ls_ln_avgpx) < trainingPeriod:
            return (None,None)

        py_ls_date = py_ls_date[-trainingPeriod:]
        py_ls_ln_avgpx = py_ls_ln_avgpx[-trainingPeriod:]

        # print "%s how_many_days_bk %s barintvl %s barintvlshift %s" % (symbol,how_many_days_bk,barintvl,barintvlshift)
        # print py_ls_date
        # print py_ls_ln_avgpx

        R.r.assign('r_x',py_ls_ln_avgpx)
        R.r('r_x = sapply(r_x, as.numeric)')

        if model == B2_rpy_prediction.ARIMA:
            # py_fit = R.r('r_fit = arima(x=r_x, order=c(3,1,3))')
            py_fit = R.r('r_fit = tryCatch({arima(x=r_x, order=c(2,1,2))}, error=function(e){} )')

            if str(py_fit) == 'NULL':
                return (None,None)

            py_fit_coef = R.r('coef(r_fit)')
        elif model == self.TAYLOR:
            pass

        ###################################################
        # forecast from the latest bar, not the shifted bars
        ###################################################
        py_ls_date_tmp = py_ls_date_full[barintvlshift:-how_many_days_bk]
        py_ls_ln_avgpx_tmp = py_ls_ln_avgpx_full[barintvlshift:-how_many_days_bk]

        py_ls_date = []
        py_ls_ln_avgpx = []

        iCnt=0
        for d in reversed(py_ls_date_tmp):
            if iCnt % barintvl == 0:
                py_ls_date.append(d)
            iCnt += 1

        iCnt=0
        for p in reversed(py_ls_ln_avgpx_tmp):
            if iCnt % barintvl == 0:
                py_ls_ln_avgpx.append(p)
            iCnt += 1

        if len(py_ls_ln_avgpx) < trainingPeriod:
            return (None,None)

        py_ls_date = (list(reversed(py_ls_date)))[-trainingPeriod:]
        py_ls_ln_avgpx = (list(reversed(py_ls_ln_avgpx)))[-trainingPeriod:]

        # print "%s %s %s %s %s" % (py_ls_date[-1],py_ls_date,how_many_days_bk,barintvl,barintvlshift)

        if model == B2_rpy_prediction.ARIMA:
            R.r('fc = forecast(r_fit, h=1)')
            py_fc = R.r('fc$mean')
            fc_pxreturn = math.exp(py_fc[0] - py_ls_ln_avgpx[-1]) -1.0
            fc_pxreturn_1d = fc_pxreturn / float(barintvl)

            return (py_fit_coef, fc_pxreturn_1d)
        elif model == self.TAYLOR:
            return (None,None)
