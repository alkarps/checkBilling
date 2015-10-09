# coding=utf-8
__author__ = 'work'
import oracle11g;
import settings as st;
import logging;
import os;


if __name__ == '__main__':
    logging.basicConfig(filename=os.path.normpath(os.getcwd() + '//' + 'log.log'),
                        format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO);
    for sib in st.siberia:
        logging.info(sib[7] + ": " + str(oracle11g.getResult(sib[0],sib[1],sib[2],sib[3],sib[4],sib[5],sib[6])[0][0]));