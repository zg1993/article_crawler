# -*- coding: utf-8 -*-

from pprint import pprint
import re
import time
import asyncio
import aiohttp
import requests
from datetime import datetime
from crawler.parse_html import parse_toutian_pages, parse_toutian_article
from crawler.utils import str_to_timestamp, get_time_now, app_log
from crawler.aiohttp_fetch import fetch
from common.const import TOUTIAO_COOKIE

cookie_str = 'tt_webid=7256623115072669244; _ga=GA1.1.1342661671.1689564238; _S_DPR=1.100000023841858; _S_IPAD=0; s_v_web_id=verify_lk6axewo_xe1UmQ1q_sz3m_4W4X_AAGk_uXqoNYVzJPYz; passport_csrf_token=89652ef7836c868340dfee91acedfeb6; passport_csrf_token_default=89652ef7836c868340dfee91acedfeb6; _tea_utm_cache_4916=undefined; notRedShot=1; msToken=HAT4N_RiFf4ufAjM0VWdo6txI84c5SMXXjXVilysI9tygLSh5ozcqNT8M-navWqd_fx1xgcUSU4kCIHDQkBHktlENL3fwUsJ1qX2Sz9C; _ga_QEHZPBE5HH=GS1.1.1690941264.4.1.1690942791.0.0.0; ttwid=1%7CBipf-RXAHqM_71rGvq1gc2XrXjK9UACVk7jxKc5j1vg%7C1690942792%7Ce9c2ae1206e0b6c1647ac6f664ef06811e39e0705366235b382bd03f3922b659; _S_WIN_WH=1447_862'


def test():
    from crawler.article import load_cookies
    cookie = load_cookies(cookie_str)
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    params = {
        'dvpf': 'pc',
        'source': 'search_subtab_switch',
        'keyword': '双碳',
        'pd': 'synthesis',
        'action_type': 'search_subtab_switch',
        'from': 'search_tab',
        'cur_tab_title': 'search_tab',
        'filter_vendor': 'all',
        'index_resource': 'all',
        'filter_period': 'day',
        'min_time': '1690871501',
        'max_time': '1690957901'
    }
    url = 'https://so.toutiao.com/search'
    res = requests.get(url=url, cookies=cookie, params=params)
    app_log.info(len(res.text))
    parse_toutian_pages(res.text)
    # url = 'https://so.toutiao.com/search/jump?url=http%3A%2F%2Fwww.toutiao.com%2Fa7262293013651522105%2F%3Fchannel%3D%26source%3Dsearch_tab&aid=4916&jtoken=e5cb68446a79ba5d6b844e3a2da048e73a56fcd37db8a9f492af34c6cdf30f4c2cc0773bd0b6e3e55553025d9a1f7754bf6e7e1026ed9c59e50e84cdeececaf1'
    # response = requests.get(url=url, cookies=cookie, headers=headers)
    # app_log.info(len(response.text))
    # article_dict = parse_toutian_article(response.text)
    # if article_dict:
    #     pass
    # app_log.info(response.url)


async def main(now_str, search_keys=['双碳'], redis_cli=None, **kwargs):
    try:
        global cookie_str
        if redis_cli and redis_cli.get(TOUTIAO_COOKIE):
            cookie_str = redis_cli.get(TOUTIAO_COOKIE)
        headers = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Cookie': cookie_str
        }
        # cookie = load_cookies(cookie_str)
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        if start_time and end_time:
            min_time = str_to_timestamp(start_time, '%Y-%m-%d')
            max_time = str_to_timestamp(end_time, '%Y-%m-%d') + 60 * 60 * 24
        else:
            # 备用
            # max_time = str_to_timestamp(now_str)
            # min_time = max_time - 60 * 60 * 24

            min_time = str_to_timestamp(now_str, '%Y-%m-%d')
            max_time = min_time + 60 * 60 * 24
            # min_time = 0
            app_log.info(f'{min_time}-{max_time}')
            app_log.info(datetime.fromtimestamp(max_time))
        async with aiohttp.ClientSession(headers=headers) as session:
            search_url = 'https://so.toutiao.com/search'
            article_arr = []
            for search in search_keys:
                assert search
                params = {
                    'dvpf': 'pc',
                    'source': 'search_subtab_switch',
                    # 'source': 'input',
                    'keyword': f'{search}',
                    'pd': 'synthesis',
                    'action_type': 'search_subtab_switch',
                    'from': 'search_tab',
                    'cur_tab_title': 'search_tab',
                    'filter_vendor': 'site',
                    'index_resource': 'site',
                    'filter_period': 'day',
                    'min_time': f'{min_time}',
                    'max_time': f'{max_time}'
                }
                # search_response = await fetch(session ,search_url, params=params, is_json=False)
                search_response = await fetch(session ,search_url, is_json=False, params=params)
                # async with session.get(url=search_url, params=params) as resp:
                #     data = await resp.text()
                #     pass
                #     search_result_arr = parse_toutian_pages(data)
                search_result_arr = parse_toutian_pages(search_response)
                app_log.info(search_result_arr)
                article_arr.extend(search_result_arr)
            app_log.info(article_arr)
            link_task = []
            for article in article_arr:
                link = article['link']
                link_task.append(
                    asyncio.create_task(fetch(session, link, is_json=False))
                )
            res = []
            content_arr = await asyncio.gather(*link_task)
            for index, content_html in enumerate(content_arr):
                article_dict = parse_toutian_article(content_html)
                if article_dict is not None:
                    # link title cover update_time content extracted_from aid(Lack: topic)
                    ele = dict(article_arr[index], **article_dict)
                    # del ele['content']
                    res.append(ele)
            app_log.info([i.get('title') for i in res])
            return res
    except Exception as e:
        app_log.error(e)
        return None
   

if __name__ == '__main__':
    now_str = get_time_now('%Y-%m-%d %H:%M:%S')
    asyncio.run(main(now_str))
    # test()
