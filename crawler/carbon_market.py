# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from crawler.parse_html import parse_carbon_market


async def main(*args, **kwargs):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    }
    url = 'https://carbonmarket.cn/ets/cets/'
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                carbon_html = await resp.text()
                data = parse_carbon_market(carbon_html)
                print(data)
                return data
                # if arr is None:
                #     pass
                # else:
                #     pass

        


if __name__ == '__main__':
    asyncio.run(main())