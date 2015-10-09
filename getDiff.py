# coding=utf-8
__author__ = 'work'
import oracle11g
import settings as st
import logging
import os

def getInfo(login, password, host, port, sid, servicename, query):
    dicResult = {}
    result = oracle11g.getResult(login, password, host, port, sid, servicename, query)
    for row in result:
        dicResult[str(row[0])] = row[1]
    return dicResult

def diff_old(startDic, dwhDic):
    result = {}
    for key in startDic.keys():
        if key not in dwhDic:
            result[key] = (startDic[key], 0)
        else:
            if startDic[key] != dwhDic[key]:
                result[key] = (startDic[key], dwhDic[key])
            dwhDic.pop(key)
    if len(dwhDic) != 0:
        for key in dwhDic.keys():
            result[key] = (0, dwhDic[key])
    return result

if __name__ == '__main__':
    logging.basicConfig(filename=os.path.normpath(os.getcwd() + '//' + 'log.log'),
                        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO)
    logging.info('start getting info from start')
    startDic = getInfo(st.start[0],st.start[1],st.start[2],st.start[3],st.start[4],st.start[5],st.start[6])
    logging.info('finish getting info from start')
    logging.info('start getting info from dwh')
    dwhDic = getInfo(st.dwh_diff[0],st.dwh_diff[1],st.dwh_diff[2],st.dwh_diff[3],st.dwh_diff[4],st.dwh_diff[5],st.dwh_diff[6])
    logging.info('finish getting info from dwh')
    logging.info('start diffing')
    _result = diff_old(startDic,dwhDic)
    logging.info('finish diffing')
    logging.info('start formatting result')
    keys = _result.keys()
    result = ''
    listClients = None
    for key in keys:
        result+= 'clientId: ' + str(key) + ' count in start: ' + str(_result[key][0]) \
                 + ' count in dwh: ' + str(_result[key][1]) + '\n'
        if listClients is None:
            listClients = str(key)
        else:
            listClients+=",{0}".format(str(key))
    logging.info('finish formatting result')
    logging.info('result:\n%s',result)
    logging.info('list clients:\n%s',key)