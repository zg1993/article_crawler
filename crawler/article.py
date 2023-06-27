# -*- coding: utf-8 -*-

import sys
import os
import re
import asyncio
import aiohttp
import json
from crawler.utils import timestamp_to_str, write_file
from crawler.parse_html import parese_wexin_article
# test
from crawler.utils import logger_config
from pprint import pprint
# flaskr
from flaskr.model import Article
from sqlalchemy import func


app_log = logger_config(log_path='/var/log/crawler/crawler_log.txt', logging_name='crawler')

# 时间取updatetime

g_search_key = ['比亚迪', '半月谈']
# search_key = ['比亚迪']

g_token = ''
g_cookie_str = 'appmsglist_action_3928503461=card; noticeLoginFlag=1; remember_acct=604328914%40qq.com; pgv_pvid=2924024080; pac_uid=0_050e9ae06ea51; tvfe_boss_uuid=890b429a39ebc7ca; RK=Gelp6pi4Xf; ptcz=66aa14b01a2ea41e402cfba10b10b07334b9709205e4229b0df45cf26d1a7997; fqm_pvqid=8197a091-1292-41b4-8874-b5719a04e115; ptui_loginuin=604328914; ua_id=jW09Y9qMMJuUgdQ1AAAAANDk3XKvP74QfmGGFt4DCq0=; wxuin=86107293996414; mm_lang=zh_CN; noticeLoginFlag=1; cert=9bBIg6HXL0ZvmwL9lmZAsF7eQEceSzfd; _clck=3928503461|1|fcr|0; uuid=8abd1b0f3452eb0a438757ba1726a0c2; bizuin=3928503461; ticket=6f090ad342a5ffc1312c3fde61ffc2352f48c030; ticket_id=gh_9b10aff30334; slave_bizuin=3928503461; rand_info=CAESIMV9caHy/7MNPw3a0GgAbHrFd0kBbAygbc/Vrmyx4KiC; data_bizuin=3928503461; data_ticket=Y9NEs5Nn52v8qyoKMhbKS8h6ARMu7E2PF7jhYpgmfQh98xkoGemhCtQBpj3sjSvC; slave_sid=UlpxSHJYVmpfcG9GMDNjRkNzZDI0Rm1YcVhRMFo4eGU2YUZTNF9JVHF2cnYzRUw1UTVnaGptRjNJMU5XMFpPSGpXYmZRbmNRQlZObElrZTI1R2lIQWtpU2pKd0dHc2VVbDdlZGxSaGtpQkhEU00wZVpXOWJjQXZLZ0c3OWwxQ0pERzNPRzIwaHBKdHVxSDJR; slave_user=gh_9b10aff30334; xid=9c3b8cb6836f39a19c8a5b7c36899b77; openid2ticket_opTQo6rYA33kqeYqkKRaa0BAPji4=YFxS4/EMPWyWgWABCQnbRAe8BjHejO4hvkvjfMZjS0w=; _clsk=1togqf9|1687655324343|7|1|mp.weixin.qq.com/weheat-agent/payload/record'
# g_cookie_str = 'pgv_pvid=2924024080; pac_uid=0_050e9ae06ea51; tvfe_boss_uuid=890b429a39ebc7ca; RK=Gelp6pi4Xf; ptcz=66aa14b01a2ea41e402cfba10b10b07334b9709205e4229b0df45cf26d1a7997; fqm_pvqid=8197a091-1292-41b4-8874-b5719a04e115; ptui_loginuin=604328914; ua_id=jW09Y9qMMJuUgdQ1AAAAANDk3XKvP74QfmGGFt4DCq0=; wxuin=86107293996414; mm_lang=zh_CN; noticeLoginFlag=1; cert=9bBIg6HXL0ZvmwL9lmZAsF7eQEceSzfd; _clck=3928503461|1|fcr|0; uuid=8abd1b0f3452eb0a438757ba1726a0c2; bizuin=3928503461; ticket=6f090ad342a5ffc1312c3fde61ffc2352f48c030; ticket_id=gh_9b10aff30334; slave_bizuin=3928503461; rand_info=CAESIMV9caHy/7MNPw3a0GgAbHrFd0kBbAygbc/Vrmyx4KiC; data_bizuin=3928503461; data_ticket=Y9NEs5Nn52v8qyoKMhbKS8h6ARMu7E2PF7jhYpgmfQh98xkoGemhCtQBpj3sjSvC; slave_sid=UlpxSHJYVmpfcG9GMDNjRkNzZDI0Rm1YcVhRMFo4eGU2YUZTNF9JVHF2cnYzRUw1UTVnaGptRjNJMU5XMFpPSGpXYmZRbmNRQlZObElrZTI1R2lIQWtpU2pKd0dHc2VVbDdlZGxSaGtpQkhEU00wZVpXOWJjQXZLZ0c3OWwxQ0pERzNPRzIwaHBKdHVxSDJR; slave_user=gh_9b10aff30334; xid=9c3b8cb6836f39a19c8a5b7c36899b77; openid2ticket_opTQo6rYA33kqeYqkKRaa0BAPji4=YFxS4/EMPWyWgWABCQnbRAe8BjHejO4hvkvjfMZjS0w=; _clsk=1hq4e12|1687660203545|5|1|mp.weixin.qq.com/weheat-agent/payload/record'
# g_cookie_str = 'appmsglist_action_3928503461=card; noticeLoginFlag=1; remember_acct=604328914%40qq.com; pgv_pvid=2924024080; pac_uid=0_050e9ae06ea51; tvfe_boss_uuid=890b429a39ebc7ca; RK=Gelp6pi4Xf; ptcz=66aa14b01a2ea41e402cfba10b10b07334b9709205e4229b0df45cf26d1a7997; fqm_pvqid=8197a091-1292-41b4-8874-b5719a04e115; ptui_loginuin=604328914; ua_id=jW09Y9qMMJuUgdQ1AAAAANDk3XKvP74QfmGGFt4DCq0=; wxuin=86107293996414; mm_lang=zh_CN; noticeLoginFlag=1; uuid=5413e1d3af9e84860779eee51e0da489; bizuin=3928503461; ticket=1052808daaa6b600220d3d72001169fb15606c3f; ticket_id=gh_9b10aff30334; slave_bizuin=3928503461; cert=9bBIg6HXL0ZvmwL9lmZAsF7eQEceSzfd; rand_info=CAESIPYj3AimBKobM97ESfhlxITikKChHzVihQ0OHhZet+1+; data_bizuin=3928503461; data_ticket=iZq97xJ8+bR0JQoUlAWqRNTbAejBkIsAZxXUqtF1baJp7UCFlu0o1qBLPL4MAwWA; slave_sid=TTVpc1B3ZXFRUEZWMkcyeUhoeDZUOG9MX2Z5MmR4T0c0MXNQWUtQWXV6OTZTYzNhc1lzTGtpU1c0QjNMYkpYR2VxazZqYWlRQkZKVENvMlB1WHdFS1lNdzN4SXBKb3pYVmxNSU1ZeTZSb2hDeHFjbXEwNUg5enc4SkloejNYbUN1VUpoOFplMExLbkx5b2th; slave_user=gh_9b10aff30334; xid=f716be5a9053d0f2ea04fc56e19de515; openid2ticket_opTQo6rYA33kqeYqkKRaa0BAPji4=wV3KuKg3i27VEmNHiN6wB64BB5ZeYnHXfigAlMdxZCs=; _clck=3928503461|1|fcm|0; _clsk=m3w3wk|1687253082169|3|1|mp.weixin.qq.com/weheat-agent/payload/record'
g_cookies = {}
g_headers = {
    'accept':
    '*/*',
    'Referer':
    'https://mp.weixin.qq.com/',
    'sec-ch-ua-platform':
    "Linux",
    'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Host': 'mp.weixin.qq.com'
}

g_count = 20

def load_cookies():
    import urllib
    global g_cookie_str, g_cookies
    prog = re.compile(r'\s?(?P<key>.*?)=(?P<val>.*)\s?')
    for item in g_cookie_str.split(';'):
        key, val = prog.match(item).groups()
        g_cookies[key] = val
        # if 'pgv_pvid' == key:
        #     g_cookies[key] = urllib.parse.unquote(val)

async def get_token(session: aiohttp.ClientSession):
    global g_headers, g_cookies
    load_cookies()
    # print('cookies--:', g_cookies)
    url = 'https://mp.weixin.qq.com'
    async with session.get(url=url,headers=g_headers) as resp:
        print(str(resp.url))
        if 200 == resp.status:
            token = re.findall(r'.*?token=(\d+)', str(resp.url))
            if token:
                token = token[0]
                return token
            else:
                app_log.warning('登录失败')
                return
def get_token1():
    import requests
    global headers, cookies
    load_cookies()
    url = 'https://mp.weixin.qq.com'
    res = requests.Session().get(url=url, headers=g_headers,cookies=g_cookies, verify=False)
    app_log.info(res.url)
    # app_log.info(res.url)
    app_log.info(res.status_code)
    return re.findall(r'.*?token=(\d+)', res.url)
    # app_log.info(res.links)



def print_dict(d):
    print(json.dumps(d, indent=4, ensure_ascii=False))


async def fetch(session, url, is_json=True, **kwargs):
    async with session.get(url, **kwargs) as resp:
        if resp.status != 200:
            resp.raise_for_status()
        if is_json:
            data = await resp.json()
        else:
            data = await resp.text()
        return data


async def fetch_multi_fakeid(session, search_arr, headers, cookies,token):
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


async def init_fakeid(session, headers, cookies,token):
    global g_search_key
    search_key = g_search_key
    search_res = await fetch_multi_fakeid(session, search_key, headers,cookies, token)
    print('init_fakeid: ',search_res)
    fakeid_arr = []
    for index, res in enumerate(search_res):
        name = search_key[index]
        if not res.get('list'):
            print(res)
        arr = res['list']
        if len(arr):
            selected = arr[0]
            print('关键字<{0}>搜索结果：{1}'.format(name, selected['nickname']))
            print('介绍 {}'.format(selected.get('signature')))
            fakeid_arr.append(selected['fakeid'])
        else:
            print('无法搜索到 {}, 请重新确认关键字'.format(name))
    return fakeid_arr


async def fetch_multi_articles(session,
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
    # print(results)
    print('resutls-len', len(results))
    return results


def handle_articles_arr(arrs):
    result = []
    for arr in arrs:
        articles = arr.get('app_msg_list', [])
        print('articles len', len(articles))
        for article in articles:
            update_time = article['update_time']
            title = article['title']
            link = article['link']
            cover = article['cover']
            aid = article['aid']
            # display_time = timestamp_to_str(update_time)
            result.append({
                'aid': aid,
                'title': title,
                'link': link,
                'update_time': update_time,
                'cover': cover,
                # 'display_time': display_time,
            })
            
    print('res sum: ', len(result))
    return result

async def fetch_content(arr, session, **kwargs):
    tasks_link = []
    for article in arr:
        link = article['link']
        tasks_link.append(asyncio.create_task(parse_wexin_article(session, link, **kwargs)))
    res = await asyncio.gather(*tasks_link)
    for index, content in enumerate(res):
        arr[index]['content'] = content
        print(arr[index]['title'], len(content), type(content))
    return arr

async def parse_wexin_article(session, url, **kwargs):
    html_text = await fetch(session, url, is_json=False, **kwargs)
    new_html = parese_wexin_article(html_text)
    return new_html
    # path = '/home/zg/Documents/gftPackage/{}.html'.format('1.html')
    # write_file(path, html_text)


async def main(db=None):
    # test
    insert_data = []
    # for i in 
    # if db:
    #     for item in insert_data:
    #         item['content'] = "<h1>wode</h1>"
    #         art = Article(**item)
    #         db.session.add(art)
    #     # print('end commit ----')
    #     print('start commit ----')
    #     try:
    #         db.session.commit()
    #     except Exception as e:
    #         print('error: ', e)
    #     finally:
    #         print('commit end ----')

    print('start main----------')
    insert_data = []
    global g_token, g_headers, g_cookies
    load_cookies()
    async with aiohttp.ClientSession() as session:
        g_token = get_token1()
        # g_token = await get_token(session)
        # app_log.info(g_token)
        # if not g_token:
        #     # pass
        #     return
        g_headers['cookie'] = g_cookie_str
        fakeid_arr = ['MzkzNjIwODU5OA==', 'MjM5OTU4Nzc0Mg==']
        # fakeid_arr = await init_fakeid(session, g_headers, g_cookies, g_token)
        print('fakeid_arr: ', fakeid_arr)
        articles_arr = await fetch_multi_articles(session, fakeid_arr, g_headers,g_cookies, g_token)
        result =  handle_articles_arr(articles_arr)
        arr = await fetch_content(result, session)
        # pprint([(i['title'], i['aid'], i['link']) for i in arr])
        print('arr', len(arr))
        insert_data = arr
        # print('arr', arr)
    if db:
        for item in insert_data:
            art = Article(**item)
            db.session.add(art)
        print('start commit ----')
        try:
            db.session.commit()
        except Exception as e:
            print('error: ', e,)
        finally:
            print('commit end ----')

        

if __name__ == '__main__':
    asyncio.run(main(db=None))
    # load_cookies()
    # get_token1()