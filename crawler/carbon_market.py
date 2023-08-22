# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from crawler.parse_html import (parse_carbon_market, parse_carbon_market_gz,
                                parse_carbon_market_hb, parse_carbon_market_sz,
                                parse_carbon_market_bj)
from crawler.aiohttp_fetch import fetch, post

from enum import Enum


class CarbonMarket(Enum):
    QUANGUO = 'QG'
    GUANGZHOU = 'GZ'
    HUBEI = 'HB'
    SHENZHEN = 'SZ'
    BEIJING = 'BJ'


CarbonMarket.QUANGUO.parse = parse_carbon_market
CarbonMarket.GUANGZHOU.parse = parse_carbon_market_gz
CarbonMarket.HUBEI.parse = parse_carbon_market_hb
CarbonMarket.SHENZHEN.parse = parse_carbon_market_sz
CarbonMarket.BEIJING.parse = parse_carbon_market_bj
CarbonMarket.GUANGZHOU.params = {
    "Top": "1",
    "beginTime": "2023-08-01",
    "endTime": "2030-09-12",
}


async def main(*args, **kwargs):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    # url_qg = 'https://carbonmarket.cn/ets/cets/' # 全国
    urls = {
        CarbonMarket.QUANGUO :'https://carbonmarket.cn/ets/cets/', # 全国
        CarbonMarket.GUANGZHOU:
        'http://ets.cnemission.com/carbon/portalIndex/markethistory',  # 广州'https://www.cnemission.com/article/hqxx/' 17:00之前就有数据
        CarbonMarket.HUBEI:
        'http://www.hbets.cn/list/13.html',
        CarbonMarket.SHENZHEN:
        'https://new.szets.com/api/v1/cerx/deal-data/page',
        # CarbonMarket.BEIJING: 'https://www.bjets.com.cn/article/jyxx/',
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        result = []
        task = []
        keys = []
        for key, url in urls.items():
            params = getattr(key, 'params', None)
            keys.append(key)
            if key == CarbonMarket.SHENZHEN:
                headers = {'Content-type': 'application/json'}
                data = {
                    'businessType': 'dealData',
                    'page': 0,
                    'productName': 'SZEA',
                    'size': 10
                }
                task.append(
                    asyncio.create_task(
                        post(session, url, headers=headers, json=data)))
            else:
                task.append(
                    asyncio.create_task(
                        fetch(session, url, is_json=False, params=params)))
        html_list = await asyncio.gather(*task)
        for index, html_text in enumerate(html_list):
            key = keys[index]
            func = key.parse
            if func and callable(func):
                result.append(func(html_text, key.value))
        print(result)
        return result

        # async with session.get(url_qg) as resp:
        #     if resp.status == 200:
        #         carbon_html = await resp.text()
        #         data = parse_carbon_market(carbon_html)
        #         print(data)
        #         return data


if __name__ == '__main__':
    asyncio.run(main())