# -*-coding: utf-8 -*-

import pytz
import os
import logging


def logger_config(log_path,logging_name):
    '''
    配置log
    :param log_path: 输出log路径
    :param logging_name: 记录中name，可随意
    :return:
    '''
    '''
    logger是日志对象，handler是流处理器，console是控制台输出（没有console也可以，将不会在控制台输出，会在日志文件中输出）
    '''
    # 获取logger对象,取名
    logger = logging.getLogger(logging_name)
    # 输出DEBUG及以上级别的信息，针对所有输出的第一层过滤
    logger.setLevel(level=logging.DEBUG)
    # 获取文件日志句柄并设置日志级别，第二层过滤
    handler = logging.FileHandler(log_path, encoding='UTF-8')
    handler.setLevel(logging.INFO)
    # 生成并设置文件日志格式
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s - %(lineno)s]  %(message)s')
    handler.setFormatter(formatter)
    # console相当于控制台输出，handler文件输出。获取流句柄并设置日志级别，第二层过滤
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # 为logger对象添加句柄
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger
 

def timestamp_to_str(timestamp):
    tz = pytz.timezone('Asia/Shanghai')
    return pytz.datetime.datetime.fromtimestamp(timestamp,tz).strftime('%Y-%m-%d %H:%M')
    

def write_file(path, content):
    if os.path.exists(path):
        raise KeyError('{} already exist'.format(path))
    with open(path, 'w+') as f:
        f.write(content)

if __name__ == "__main__":
    logger = logger_config(log_path='/var/log/crawler/gft_log.txt', logging_name='version')
    logger_test = logger_config(log_path='log1.txt', logging_name='test')
    logger.info("sssss是是是")
    logger.error("是是是error")
    logger.debug("是是是debug")
    logger.warning("是是是warning")
    print('print和logger输出是有差别的！')
    # logger_test.info('11')