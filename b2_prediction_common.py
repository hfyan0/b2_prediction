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
        
        self.MaxBarIntervalArima  = int(config.get("ARIMA", "MaxBarInterval"))
        self.CoefFolderArima      =     config.get("ARIMA", "CoefFolder"    )
        self.ForecastFolderArima  =     config.get("ARIMA", "ForecastFolder")

        self.MaxBarIntervalTaylor = int(config.get("Taylor", "MaxBarInterval"))
        self.CoefFolderTaylor     =     config.get("Taylor", "CoefFolder"    )
        self.ForecastFolderTaylor =     config.get("Taylor", "ForecastFolder")

        ###################################################
        self.prev_forecasts_arima = {}
        self.prev_forecasts_taylor = {}

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

    def load_prev_forecasts(self):
        filelist = [ f for f in listdir(self.ForecastFolderArima) if isfile(join(self.ForecastFolderArima,f)) ]
        # print filelist
        for symfile in filelist:
            ###################################################
            # FIXME: right now there will be no result if it wasn't already in the file
            ###################################################
            with open(self.ForecastFolderArima+'/'+symfile,'r') as f:
                print f
                for line in f:
                    csv = line.strip().split(",")
                    if len(csv) < 6:
                        continue

                    dt = datetime.strptime(csv[0],"%Y-%m-%d").date()
                    sym = csv[1]
                    barintvl_shift = csv[3]+'_'+csv[4]
                    fcast = float(csv[5])

                    if sym not in self.prev_forecasts_arima:
                        self.prev_forecasts_arima[sym] = {}

                    if dt not in self.prev_forecasts_arima[sym]:
                        self.prev_forecasts_arima[sym][dt] = {}

                    self.prev_forecasts_arima[sym][dt][barintvl_shift] = fcast


        filelist = [ f for f in listdir(self.ForecastFolderTaylor) if isfile(join(self.ForecastFolderTaylor,f)) ]
        # print filelist
        for symfile in filelist:
            ###################################################
            # FIXME: right now there will be no result if it wasn't already in the file
            ###################################################
            with open(self.ForecastFolderTaylor+'/'+symfile,'r') as f:
                for line in f:
                    csv = line.strip().split(",")
                    if len(csv) < 6:
                        continue

                    dt = datetime.strptime(csv[0],"%Y-%m-%d").date()
                    sym = csv[1]
                    barintvl_shift = csv[3]+'_'+csv[4]
                    fcast = float(csv[5])

                    if sym not in self.prev_forecasts_taylor:
                        self.prev_forecasts_taylor[sym] = {}

                    if dt not in self.prev_forecasts_taylor[sym]:
                        self.prev_forecasts_taylor[sym][dt] = {}

                    self.prev_forecasts_taylor[sym][dt][barintvl_shift] = fcast

    def get_prev_forecast(self, dt, sym, model):
        agg_fcast = 0.0

        # print "model = %s" % (model)
        if model == B2_rpy_prediction.ARIMA:
            if dt not in self.prev_forecasts_arima[sym]:
                return None
            if sym not in self.prev_forecasts_arima:
                return None
        elif model == B2_rpy_prediction.TAYLOR:
            if dt not in self.prev_forecasts_taylor[sym]:
                return None
            if sym not in self.prev_forecasts_taylor:
                return None

        barintvl_cnt = []
        barintvl_tot1drtn = []

        for barintvl in range(50):
            barintvl_cnt.append(0)
            barintvl_tot1drtn.append(0)

        if model == B2_rpy_prediction.ARIMA:
            iteri = self.prev_forecasts_arima[sym][dt].iteritems()
        elif model == B2_rpy_prediction.TAYLOR:
            iteri = self.prev_forecasts_taylor[sym][dt].iteritems()

        for k,v in iteri:
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

    ###################################################
    # an important function that calibrates our models and make forecast
    ###################################################
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
            ###################################################
            # construct the Taylor terms
            ###################################################
            py_ls_rev_avgpx = list(reversed(map(lambda x: math.exp(x), py_ls_ln_avgpx)))
            py_ls_rev_date = list(reversed(py_ls_date))

            py_ls_rev_avgpx_d = []
            py_ls_rev_avgpx_dd = []
            py_ls_rev_date_d = []
            py_ls_rev_date_dd = []

            if len(py_ls_rev_avgpx) <= 2:
                return (None,None)

            for i in range(len(py_ls_rev_avgpx)-1):
                py_ls_rev_avgpx_d.append(py_ls_rev_avgpx[i]-py_ls_rev_avgpx[i+1])
                py_ls_rev_date_d.append(py_ls_rev_date[i]+"-"+py_ls_rev_date[i+1])
            for i in range(len(py_ls_rev_avgpx_d)-1):
                py_ls_rev_avgpx_dd.append(py_ls_rev_avgpx_d[i]-py_ls_rev_avgpx_d[i+1])
                py_ls_rev_date_dd.append(py_ls_rev_date_d[i]+"-"+py_ls_rev_date_d[i+1])

            py_ls_rev_avgpx_d_next = py_ls_rev_avgpx_d[:-3]
            py_ls_rev_avgpx = py_ls_rev_avgpx[1:-3]
            py_ls_rev_avgpx_d = py_ls_rev_avgpx_d[1:-2]
            py_ls_rev_avgpx_dd = py_ls_rev_avgpx_dd[1:-1]

            py_ls_rev_date_d_next = py_ls_rev_date_d[:-3]
            py_ls_rev_date = py_ls_rev_date[1:-3]
            py_ls_rev_date_d = py_ls_rev_date_d[1:-2]
            py_ls_rev_date_dd = py_ls_rev_date_dd[1:-1]

            # print ""
            # print "py_ls_rev_date_d_next %s " % py_ls_rev_date_d_next
            # print "py_ls_rev_date        %s " % py_ls_rev_date
            # print "py_ls_rev_date_d      %s " % py_ls_rev_date_d
            # print "py_ls_rev_date_dd     %s " % py_ls_rev_date_dd

            R.r.assign('r_rev_avgpx_d_next',py_ls_rev_avgpx_d_next)
            R.r.assign('r_rev_avgpx',py_ls_rev_avgpx)
            R.r.assign('r_rev_avgpx_d',py_ls_rev_avgpx_d)
            R.r.assign('r_rev_avgpx_dd',py_ls_rev_avgpx_dd)
            R.r('r_rev_avgpx_d_next = sapply(r_rev_avgpx_d_next, as.numeric)')
            R.r('r_rev_avgpx = sapply(r_rev_avgpx, as.numeric)')
            R.r('r_rev_avgpx_d = sapply(r_rev_avgpx_d, as.numeric)')
            R.r('r_rev_avgpx_dd = sapply(r_rev_avgpx_dd, as.numeric)')

            py_fit = R.r('r_fit = tryCatch({lm(r_rev_avgpx_d_next ~ r_rev_avgpx_d + r_rev_avgpx_dd)}, error=function(e){} )')

            if str(py_fit) == 'NULL':
                return (None,None)

            py_fit_coef = R.r('coef(r_fit)')

        ###################################################
        # forecast from the latest bar, not the shifted bars
        ###################################################
        py_ls_date_tmp = py_ls_date_full[:-how_many_days_bk]
        py_ls_ln_avgpx_tmp = py_ls_ln_avgpx_full[:-how_many_days_bk]

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

        ###################################################
        R.r.assign('r_ls_ln_avgpx',py_ls_ln_avgpx)
        R.r('r_ls_ln_avgpx = sapply(r_ls_ln_avgpx, as.numeric)')

        ###################################################
        if model == B2_rpy_prediction.ARIMA:
            # R.r('r_refit = Arima(r_ls_ln_avgpx, model=r_fit)')
            # R.r('fc = forecast(r_refit, h=1)')
            R.r('fc = forecast(r_fit, h=1)')
            py_fc = R.r('fc$mean')
            fc_pxreturn = math.exp(py_fc[0] - py_ls_ln_avgpx[-1]) -1.0
            fc_pxreturn_1d = fc_pxreturn / float(barintvl)

            return (py_fit_coef, fc_pxreturn_1d)

        elif model == B2_rpy_prediction.TAYLOR:
            py_d1 = math.exp(py_ls_ln_avgpx[-1])-math.exp(py_ls_ln_avgpx[-2])
            py_d2 = math.exp(py_ls_ln_avgpx[-1])-2*math.exp(py_ls_ln_avgpx[-2])+math.exp(py_ls_ln_avgpx[-3])

            R.r.assign('r_d1',py_d1)
            R.r('r_d1 = sapply(r_d1, as.numeric)')
            R.r.assign('r_d2',py_d2)
            R.r('r_d2 = sapply(r_d2, as.numeric)')

            py_pred = R.r('pred = predict(r_fit, data.frame(r_rev_avgpx_d = c(r_d1), r_rev_avgpx_dd = c(r_d2)))')
            fc_pxreturn_1d = py_pred[0] / math.exp(py_ls_ln_avgpx[-1]) / float(barintvl)

            return (py_fit_coef, fc_pxreturn_1d)
