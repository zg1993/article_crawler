# -*- coding: utf-8 -*-

import sys
import os
import re
import time
import asyncio
import aiohttp
import json
from datetime import datetime
from crawler.utils import timestamp_to_str, write_file, get_time_now
from crawler.parse_html import parse_wexin_article
# test
from crawler.utils import app_log
from crawler.aiohttp_fetch import fetch
from crawler.sogou import main as sogou
from common.const import SourceType
from pprint import pprint
# flaskr

from sqlalchemy import func
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import current_app
from flaskr.model import Article, Task

FAKEIDS_KEY = 'crawler:fakeids'
COOKEIS_KEY = 'crawler:cookies'

g_search_key = ['抚州发布']

g_fakeid_dict = {}
g_token = ''
g_cookie_str = 'appmsglist_action_3928503461=card; noticeLoginFlag=1; remember_acct=604328914%40qq.com; pgv_pvid=2924024080; pac_uid=0_050e9ae06ea51; tvfe_boss_uuid=890b429a39ebc7ca; RK=Gelp6pi4Xf; ptcz=66aa14b01a2ea41e402cfba10b10b07334b9709205e4229b0df45cf26d1a7997; fqm_pvqid=8197a091-1292-41b4-8874-b5719a04e115; ptui_loginuin=604328914; ua_id=jW09Y9qMMJuUgdQ1AAAAANDk3XKvP74QfmGGFt4DCq0=; wxuin=86107293996414; mm_lang=zh_CN; noticeLoginFlag=1; cert=9bBIg6HXL0ZvmwL9lmZAsF7eQEceSzfd; rewardsn=; wxtokenkey=777; wwapp.vid=; wwapp.cst=; wwapp.deviceid=; bizuin=3928503461; ticket=b472cad5681fe1d47b9c264476a072c7eb3b1e49; ticket_id=gh_9b10aff30334; slave_bizuin=3928503461; uuid=ea4fd82ecd84c9111adb94aa5ed85032; rand_info=CAESIJ48gs/Q8FqeGMpVP6lyl+yPQNyU66SxufVJ/hDSn1rT; data_bizuin=3928503461; data_ticket=qRN6wTqIA6H3UO1Ie8S4c/WtyOa/wI47vsp0UemcT110RVbiApjMGddTaDmWwtDO; slave_sid=ejQ5VWQyX0ZlX3ZBOEhpX1luVEFZWnZ0T2hJNlNad0l4bmJGUWhYRDFBdXlLYlE0dHpCUUluVG41MzdJWG9sVlNjZmRIcTVlVTk2cUptRHhMcEJpWGdTanBqUTRfQ2toQ0ZySWZ6RkNwcWRPb19tNVJvMVVSc2N6d0YxaWJtV0JLeGc4VnBNdFd6U1pHRUhS; slave_user=gh_9b10aff30334; xid=4e5d42e11c5eb6639dfdb3afc481b1f3; openid2ticket_opTQo6rYA33kqeYqkKRaa0BAPji4=Wx6NM4BLLHVIbdCjILZzLTgpE2O+AhxP2zwjB0mCVzs=; _clck=3928503461|1|fcu|0; _clsk=131sz9a|1687940181775|3|1|mp.weixin.qq.com/weheat-agent/payload/record'

g_cookies = {}
g_headers = {
    'accept': '*/*',
    'Referer': 'https://mp.weixin.qq.com/',
    'sec-ch-ua-platform': "Linux",
    'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Host': 'mp.weixin.qq.com'
}
g_redis = None

g_count = 20


def load_cookies(cookei_str):
    cookies = {}
    prog = re.compile(r'\s?(?P<key>.*?)=(?P<val>.*)\s?')
    for item in cookei_str.split(';'):
        key, val = prog.match(item).groups()
        cookies[key] = val
        # if 'pgv_pvid' == key:
        #     cookies[key] = urllib.parse.unquote(val)\\
    return cookies

def get_token1(redis_cli):
    import requests
    global g_headers
    cookies = load_cookies(redis_cli.get(COOKEIS_KEY))
    # app_log = current_app.logger
    url = 'https://mp.weixin.qq.com'
    res = requests.Session().get(url=url,
                                 headers=g_headers,
                                 cookies=cookies,
                                 verify=False)
    return re.findall(r'.*?token=(\d+)', res.url)
    


def print_dict(d):
    print(json.dumps(d, indent=4, ensure_ascii=False))


async def fetch_multi_fakeid(session, search_arr, headers, cookies, token):
    url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
    tasks = []
    for key in search_arr:
        params = {
            'action': 'search_biz',
            'begin': '0',
            'count': '5',
            'query': key,
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
        }
        tasks.append(
            asyncio.create_task(
                fetch(session, url, headers=headers, params=params)))
    results = await asyncio.gather(*tasks)
    return results


async def init_fakeid(session, headers, cookies, token, search_key_fakeid,
                      redis_cli):
    search_res = await fetch_multi_fakeid(session, search_key_fakeid, headers,
                                          cookies, token)
    store = {}
    for index, res in enumerate(search_res):
        name = search_key_fakeid[index]
        if not res.get('list'):
            print(res)
        arr = res['list']
        if len(arr):
            selected = arr[0]
            print('关键字<{0}>搜索结果：{1}'.format(name, selected['nickname']))
            print('介绍 {}'.format(selected.get('signature')))
            store[name] = json.dumps({
                'fakeid': selected['fakeid'],
                'nickname': selected['nickname'],
                'service_type': selected['service_type'],
                'signature': selected['signature'],
            })
        else:
            print('无法搜索到 {}, 请重新确认关键字'.format(name))
    redis_cli.hset(FAKEIDS_KEY, mapping=store)


async def fetch_multi_articles_by_counts(session,
                                         fakeid_arr,
                                         headers,
                                         cookies,
                                         token,
                                         article_search_key='实力'):
    global g_count
    count_article = 0
    begin = 0
    results = []
    while count_article <= g_count:
        url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
        tasks = []
        for fakeid in fakeid_arr:
            params = {
                'action': 'list_ex',
                'begin': begin,
                'count': '5',
                'fakeid': fakeid,
                'type': '9',
                'query': article_search_key,
                'token': token,
                'lang': 'zh_CN',
                'f': 'json',
                'ajax': '1',
            }
            tasks.append(
                asyncio.create_task(
                    fetch(session, url, headers=headers, params=params)))
        begin = begin + 5
        res = await asyncio.gather(*tasks)
        # 如果所有公众号返回都是[]则停止检索
        count = sum([len(i.get('app_msg_list', [])) for i in res])
        if 0 == count:
            break
        results.extend(res)
        count_article = count_article + count
    print('article sum: ', count_article)
    print('resutls-len', len(results))
    return results


async def fetch_articles_minunit(session, fakeid, official_account, headers,
                                 cookies, token, search_key, now_str, **kwargs):
    # count_article = 0
    begin = 0
    results = []
    last_time = '9'
    url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
    start_time = kwargs.get('start_time')
    end_time = kwargs.get('end_time')
    if start_time and end_time:
        app_log.info(f'start_time: {start_time}')
        app_log.info(f'end_time: {end_time}')
    else:
        start_time = now_str
        end_time = '9'
    while last_time >= start_time:
        params = {
            'action': 'list_ex',
            'begin': begin,
            'count': '5',
            'fakeid': fakeid,
            'type': '9',
            'query': search_key,
            'token': token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1',
        }
        res = await fetch(session, url, headers=headers, params=params)
        # 如果所有公众号返回都是[]则停止检索
        app_msg_list = res.get('app_msg_list', [])
        # print('len app_msg_list', len(app_msg_list))
        begin = begin + 5
        if 0 == len(app_msg_list):
            print(res)
            break
        last_record = app_msg_list[0]
        last_time = timestamp_to_str(last_record['update_time'],
                                     fmt='%Y-%m-%d')
        # count_article = count_article + len(app_msg_list)
        for article in app_msg_list:
            update_time = article['update_time']
            update_time_str = timestamp_to_str(update_time, fmt='%Y-%m-%d')
            # app_log.info(f'{official_account}: update_time: {update_time_str}')
            # app_log.info(update_time_str >= start_time)
            # app_log.info(update_time_str <= end_time)
            if update_time_str >= start_time and update_time_str <= end_time:
                article['extracted_from'] = official_account
                results.append(article)

    app_log.info('{0} {1}-{2}: {3}'.format(now_str, fakeid, search_key,
                                           len(results)))
    return results


async def fetch_multi_articles_unit(session,
                                    fakeid_dict,
                                    headers,
                                    cookies,
                                    token,
                                    now_str,
                                    article_search_key=[],
                                    delta=0, **kwargs):
    if delta or not now_str:                                   
        now_str = get_time_now(delta=delta)
    results = []
    if not len(article_search_key):
        article_search_key = ['']
    for fakeid, official_account in fakeid_dict.items():
        for search_key in article_search_key:
            res = await fetch_articles_minunit(session, fakeid,
                                               official_account, headers,
                                               cookies, token, search_key,
                                               now_str, **kwargs)
            await asyncio.sleep(5)
            results.extend(res)
    return results


def handle_articles_arr(articles, topic):
    result = []
    duplicates = set()
    for article in articles:
        update_time = article['update_time']
        title = article['title']
        link = article['link']
        cover = article['cover']
        aid = article['aid']
        extracted_from = article['extracted_from']
        if aid not in duplicates:
            duplicates.add(aid)
            # display_time = timestamp_to_str(update_time)
            result.append({
                'aid': aid,
                'title': title,
                'link': link,
                'update_time': update_time,
                'cover': cover,
                'topic': topic,
                'extracted_from': extracted_from,
                # 'display_time': display_time,
            })
    return result


async def fetch_content(arr, session, **kwargs):
    tasks_link = []
    for article in arr:
        link = article['link']
        tasks_link.append(
            asyncio.create_task(parse_article(session, link, **kwargs)))
    res = await asyncio.gather(*tasks_link)
    for index, content in enumerate(res):
        if content is None:
            print('content is None: {}'.format(arr[index].get('link', '--')))
        arr[index]['content'] = content
        # print(arr[index]['title'], len(content), type(content))
    return arr


async def parse_article(session, url, **kwargs):
    html_text = await fetch(session, url, is_json=False, **kwargs)
    # print('url: {}'.format(url))
    new_html = parse_wexin_article(html_text)
    return new_html
    # path = '/home/zg/Documents/gftPackage/{}.html'.format('1.html')
    # write_file(path, html_text)


def get_search_key_fakeid(redis_cli, arr):
    fakeid_dict = redis_cli.hgetall(FAKEIDS_KEY)
    res = []
    for name in arr:
        if name not in fakeid_dict:
            res.append(name)
    return res


def get_fakeid_dict(redis_cli, arr):
    fakeid_dict = redis_cli.hgetall(FAKEIDS_KEY)
    res = {}
    for name in arr:
        detail = json.loads(fakeid_dict[name])
        res[detail['fakeid']] = name
    return res

async def crawler_sogou(task, db, now_str, redis_cli, **kwargs):
    async with aiohttp.ClientSession() as session:
        insert_arr = await sogou(now_str, task['search_keys'], redis_cli=redis_cli,**kwargs)
        tasks = []
        for article in insert_arr:
            link = article['link']
            article['topic'] = task['id']
            article['aid'] = f'{article["update_time"]}_2'
            tasks.append(asyncio.create_task(parse_article(session, link)))
        res = await asyncio.gather(*tasks)
        for index, content in enumerate(res):
            if content is None:
                print('content is None: {}'.format(insert_arr[index].get('link', '--')))
            insert_arr[index]['content'] = content
            # print(arr[index]['title'], len(content), type(content))
        execute_insert(db, insert_arr)

async def execute_task(task, db, redis_cli, now_str, **kwargs):
    source = task['source']
    if SourceType.WEIXIN == source:
        await task_unit(now_str, task, db, redis_cli, **kwargs)
    elif SourceType.SOGOU == source:
        await crawler_sogou(task, db, now_str, redis_cli,**kwargs)

async def main(db=None, redis_cli=None):
    now_str = get_time_now()
    with flask_app.app_context():
        res = Task.query.filter(Task.status == 1).all()
        task_arr = [i.to_json() for i in res]
        for task in task_arr:
            await execute_task(task, db, redis_cli, now_str)
            # source = task['source']
            # if SourceType.WEIXIN == source:
            #     await task_unit(now_str, task, db, redis_cli)
            # elif SourceType.SOGOU == source:
            #     await crawler_sogou(task, db, now_str)


async def task_unit(now_str, task, db=None, redis_cli=None, **kwargs):
    # test
    global g_token, g_headers, g_cookies, g_search_key, g_cookie_str
    insert_data = []
    # 从redis里取 g_cookie_str
    g_cookie_str = redis_cli.get(COOKEIS_KEY)
    official_accounts_list = task.get('official_accounts', g_search_key)
    search_keys = task.get('search_keys', [])
    delta = task.get('delta', 0)
    topic = task.get('id')
    print('start main----------')
    insert_data = []
    # search_name_key = g_search_key
    g_cookies = load_cookies(g_cookie_str)
    search_key_fakeid = get_search_key_fakeid(redis_cli,
                                              official_accounts_list)
    async with aiohttp.ClientSession() as session:
        g_token = get_token1(redis_cli)
        if not g_token:
            app_log.info('cookies expired')
            return
        g_headers['cookie'] = g_cookie_str
        if len(search_key_fakeid):
            await init_fakeid(session, g_headers, g_cookies, g_token,
                              search_key_fakeid, redis_cli)
        fakeid_dict = get_fakeid_dict(
            redis_cli,
            official_accounts_list)  # key: fakeid val: official_account
        print('fakeid_arr: {}'.format(fakeid_dict))
        articles_arr = await fetch_multi_articles_unit(
            session,
            fakeid_dict,
            g_headers,
            g_cookies,
            g_token,
            now_str,
            article_search_key=search_keys,
            delta=delta, **kwargs)
        print('article sum: {}'.format(len(articles_arr)))
        result = handle_articles_arr(articles_arr, topic)
        print('remove duplicates article sum: {}'.format(len(result)))
        arr = await fetch_content(result, session)
        # pprint([(i['title'], i['aid'], i['link']) for i in arr])
        # pprint([(i['title']) for i in arr])
        # insert_data = arr
        insert_data = list(filter(lambda i: i.get('content', None),
                                  arr))  # drop content is None
        # print('arr', arr)
    execute_insert(db, insert_data)

def execute_insert(db, insert_data):
     if db:
        with current_app.app_context():
            try:
                start_time = time.time()
                # return 
                with db.auto_commit_db():
                    db.session.bulk_insert_mappings(Article, insert_data)
                app_log.info('insert {0} data, spend {1} seconds'.format(
                    len(insert_data),
                    time.time() - start_time))
            except Exception as e:
                # print('insert error: {}'.format(e))
                app_log.info(e)
                handle_duplicate_key(db, insert_data)

def handle_duplicate_key(db, insert_data):
    print('--start-duplicate {}'.format(len(insert_data)))
    for item in insert_data:
        try:
            with db.auto_commit_db():
                db.session.add(Article(**item))
                print(item['title'])
        except Exception as e:
            app_log.info(e)
            print('insert error: {}'.format(item['title']))
            # print('per insert error: {}'.format(e))
            # print('error aid:{} title: {}'.format(item['aid'], item['title']))


def my_clock(db_cli, redis_cli):
    print(redis_cli.dbsize())
    print(db_cli)
    print('start: {}'.format(datetime.now()))

    # with flask_app.app_context():
    #     res = Task.query.filter(Task.status==1).all()
    #     task_arr = [i.to_json() for i in res]
    # print(task_arr)

    asyncio.run(main(db_cli, redis_cli))
    # print('end: {}'.format(datetime.now()))


if __name__ == '__main__':
    from flaskr import create_app
    flask_app = create_app(True)
    redis_cli = None
    db_cli = None
    with flask_app.app_context():
        redis_cli = current_app.extensions['redis']
        db_cli = current_app.extensions['db']
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(my_clock,
                      'cron',
                      hour=23,
                      minute=55,
                      args=[db_cli, redis_cli])
    if len(sys.argv) == 2:
        my_clock(db_cli, redis_cli)
    # scheduler.add_job(my_clock, 'interval', seconds=6, args=[db_cli, redis_cli])
    scheduler.start()