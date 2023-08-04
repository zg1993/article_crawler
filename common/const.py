# -*- coding: utf-8 -*-



class ServiceType():
    subscribe = 1 # 订阅号
    service = 2 # 服务号

class Code():
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500

class Message():
    pass


class SourceType():
    WEIXIN = '微信公众号'
    SOGOU = '搜狗微信'
    TOUTIAO = '今日头条'

SNUID_KEY = 'crawler:snuid'

TASK_SET_KEY = 'crawler:task_set'

TOUTIAO_COOKIE = 'crawler:toutiaocookie'