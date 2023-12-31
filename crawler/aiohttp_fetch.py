# -*- coding: utf-8 -*-

import aiohttp


async def fetch(session: aiohttp.ClientSession, url, is_json=True, **kwargs):
    async with session.get(url, **kwargs) as resp:
        if resp.status != 200:
            resp.raise_for_status()
        if is_json:
            data = await resp.json()
        else:
            data = await resp.text()
        return data

async def post(session: aiohttp.ClientSession, url, **kwargs):
    async with session.post(url, **kwargs) as resp:
        if resp.status != 200:
            resp.raise_for_status()
        data = await resp.json()
        return data