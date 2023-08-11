# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from crawler.parse_html import parse_carbon_market, parse_carbon_market_gz
from crawler.aiohttp_fetch import fetch

from enum import Enum


class CarbonMarket(Enum):
    QUANGUO = 'QG'
    GUANGZHOU = 'GZ'
    BEIJING = 'BJ'


CarbonMarket.QUANGUO.parse = parse_carbon_market
CarbonMarket.GUANGZHOU.parse = parse_carbon_market_gz
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
        # CarbonMarket.QUANGUO :'https://carbonmarket.cn/ets/cets/', # 全国
        CarbonMarket.GUANGZHOU:
        'http://ets.cnemission.com/carbon/portalIndex/markethistory',  # 广州'https://www.cnemission.com/article/hqxx/' 17:00之前就有数据
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        result = []
        task = []
        keys = []
        for key, url in urls.items():
            params = getattr(key, 'params', None)
            keys.append(key)
            task.append(asyncio.create_task(fetch(session, url,
                                                  is_json=False, params=params)))
        html_list = await asyncio.gather(*task)
        for index, html_text in enumerate(html_list):
            key = keys[index]
            func = key.parse
            if func and callable(func):
                result.append(func(html_text, key.value))
        print(result)
        return result

        # carbon_html = await fetch(session, url_qg, is_json=False)
        # data = parse_carbon_market(carbon_html)
        # print(data)

        # async with session.get(url_qg) as resp:
        #     if resp.status == 200:
        #         carbon_html = await resp.text()
        #         data = parse_carbon_market(carbon_html)
        #         print(data)
        #         return data


if __name__ == '__main__':
    asyncio.run(main())