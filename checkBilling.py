# coding=utf-8
import oracle11g
import settings as st
import logging
import os
from multiprocessing import Process, Manager

def getDate(wl):
    import datetime;
    from suds.client import Client
    url = "http://10.31.70.153:7049/LoadTrafficRecordsScript/LoadTrafficRecordsScript?WSDL"
    client = Client(url)
    from suds.wsse import Security
    from suds.wsse import UsernameToken
    security = Security()
    token = UsernameToken(wl[0], wl[1])
    security.tokens.append(token)
    client.set_options(wsse=security)
    client.set_options(soapheaders=wl[2])
    response = client.service.getCurrentBillingPeriod()
    if response.results.result[0].billingPeriodDate.month == datetime.date.today().month:
        return None
    else:
        return response.results.result[0].billingPeriodDate.strftime('%Y%m')

def canCloseBilling(start,dwh,queries):
    result = {}
    for query in queries:
        countInStart = oracle11g.getResult(start[0], start[1], start[2], start[3], start[4], start[5], query[1])[0][0]
        countInDWH = oracle11g.getResult(dwh[0], dwh[1], dwh[2], dwh[3], dwh[4], dwh[5], query[2])[0][0]
        if countInDWH != countInStart:
            result[query[0]] = (countInStart,countInDWH)
    return result

def checkBillingFinish(dicTable, start, dwh, wl, queries):
    logging.basicConfig(filename=os.path.normpath(os.getcwd() + '//' + 'log.log'),
                        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    name = start[6]
    try:
        logging.info("Starting checking billing for " + name)
        logging.info("Start getting Billing date for " + name)
        date = getDate(wl)
        logging.info("Finish getting Billing date for " + name)
        if date is not None:
            logging.info("Start formatting query for " + name)
            for query in queries:
                query[1] = query[1].format(date)
                query[2] = query[2].format(wl[2])
            logging.info("Finish formatting query for " + name)
            logging.info("Start getting info from " + name)
            delta = canCloseBilling(start, dwh, queries)
            logging.info("Finish getting info from " + name)
            if len(delta)==0:
                result = "{0} can close".format(name)
                if tuple(result) not in dicTable: dicTable[name] = result
            else:
                result = "{}: ".format(name)
                for key in delta.keys():
                    result += "{0} in start: {1}; in dwh: {2};\n".format(key,str(delta[key][0]),str(delta[key][1]))
                if tuple(result) not in dicTable: dicTable[name] = result
        else:
            result = "{0} now closed".format(name)
            if tuple(result) not in dicTable: dicTable[name] = result
    except Exception, exc:
        logging.error(exc)
        result = "{0} finished with errors".format(name)
        if tuple(result) not in dicTable:
            dicTable[name] = "{0} finished with error".format(name)


if __name__ == '__main__':
    logging.basicConfig(filename=os.path.normpath(os.getcwd() + '//' + 'log.log'),
                        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    processList = []
    dicTable = Manager().dict()
    # Запускаем на каждую БД свой поток.
    logging.info("Start threads")
    for setting in st.settingList:
        process = Process(target=checkBillingFinish, args=(dicTable, setting, st.dwh, st.wsSettingList[setting[6]], st.querys))
        processList.append(process)
        process.start()
    for process in processList:
        process.join()
    logging.info("Finish threads")
    keys = dicTable.keys()
    for key in keys:
        logging.info(dicTable[key])