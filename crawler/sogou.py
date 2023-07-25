# -*- coding: utf-8 -*-

import re
import time
import asyncio
import aiohttp
import requests
from pprint import pprint
import random

from crawler.utils import timestamp_to_str, get_time_now, app_log
from crawler.aiohttp_fetch import fetch
from crawler.parse_html import parse_sougou_pages, parse_wexin_article




h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
 'Cookie': 'ssuid=3662390464; SUID=7A8ABB2A492CA20A0000000063E9892F; IPLOC=CN3610; SUV=008BC68E76D4452764803734AE111982; ABTEST=7|1688720177|v1; JSESSIONID=aaacpejJR0uwk9WtBGAIy; ariaDefaultTheme=default; ariaFixed=true; ariaReadtype=1; ariaStatus=false; cuid=AAFVLU0iRgAAAAqHS2W8eQAAbgQ=; PHPSESSID=80ou0i2o55hml0u12hnaoef306; SNUID=FD9C0EACD9DCD93854BBF2B2DA4CB449; seccodeRight=success; successCount=1|Thu, 20 Jul 2023 02:08:21 GMT'}


BASE_URL = 'https://weixin.sogou.com/weixin'

re_link = re.compile(r'url \+= \'(.*)\'')

aid_keys = set()

def resolve_sogou_link(link_html):
    str_arr = re_link.findall(link_html)
    return ''.join(str_arr)


async def search_result(session: aiohttp.ClientSession, search, now_str, delta=0, **kwargs):
    if delta != 0 or not now_str:
        now_str = get_time_now(delta=delta)
    count = 0
    res = []
    while count < 10:
        count = count + 1
        params = {'query': search, 'type': '2', 'page': count}
        search_html = await fetch(session, BASE_URL, is_json=False, params=params)        
        app_log.info('search_html: {}'.format(len(search_html)))
        arr = parse_sougou_pages(search_html)
        if arr is not None:
            res.extend(arr)
        else:
            app_log.info(params)
        start = time.time()
        await asyncio.sleep(random.uniform(50,100))
        app_log.info('sleep {}'.format(time.time() - start))
    filter_arr = []
    app_log.info(len(res))
    # pprint(res)
    for i in res:
        update_time = i.get('update_time')
        if timestamp_to_str(update_time, fmt='%Y-%m-%d') >= now_str:
            link = i.get('link')
            link_html = await fetch(session, link, is_json=False)
            await asyncio.sleep(random.uniform(3, 5))
            weixin_link = resolve_sogou_link(link_html)
            if weixin_link:
                i['link'] = weixin_link
                app_log.info(f'title: {i["title"]}\n{weixin_link}')
            else:
                app_log.info('error resolve sogou link failed')
                app_log.info(link_html)
            if update_time not in aid_keys:
                aid_keys.add(update_time)
                filter_arr.append(i)
            else:
                app_log.info(f'duplicate {update_time} title: {i["title"]}  link: {weixin_link}')
    app_log.info(len(filter_arr))
    return filter_arr
    # return filter(lambda i: timestamp_to_str(i['update_time'], fmt='%Y-%m-%d') >= now_str)

async def main(now_str, search_keys=['双碳'], **kwargs):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Cookie':
            'ssuid=3662390464; SUID=7A8ABB2A492CA20A0000000063E9892F; IPLOC=CN3610; SUV=008BC68E76D4452764803734AE111982; ABTEST=7|1688720177|v1; JSESSIONID=aaacpejJR0uwk9WtBGAIy; ariaDefaultTheme=default; ariaFixed=true; ariaReadtype=1; ariaStatus=false; cuid=AAFVLU0iRgAAAAqHS2W8eQAAbgQ=; PHPSESSID=80ou0i2o55hml0u12hnaoef306; SNUID=3351C063151214EE11A6DC721500188F'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            insert_data = []
            app_log.info(f'serach_keys---: {search_keys}')
            for search in search_keys:
                assert search    
                res =  await search_result(session, search, now_str, **kwargs)
                insert_data.extend(res)
                await asyncio.sleep(1)
            return insert_data
    except Exception as e:
        app_log.info(e)
        return []

if __name__ == '__main__':
    asyncio.run(main(''))
