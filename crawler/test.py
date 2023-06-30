import asyncio
import aiohttp
import re
import requests

g_cookie_str = 'appmsglist_action_3928503461=card; noticeLoginFlag=1; remember_acct=604328914%40qq.com; pgv_pvid=2924024080; pac_uid=0_050e9ae06ea51; tvfe_boss_uuid=890b429a39ebc7ca; RK=Gelp6pi4Xf; ptcz=66aa14b01a2ea41e402cfba10b10b07334b9709205e4229b0df45cf26d1a7997; fqm_pvqid=8197a091-1292-41b4-8874-b5719a04e115; ptui_loginuin=604328914; ua_id=jW09Y9qMMJuUgdQ1AAAAANDk3XKvP74QfmGGFt4DCq0=; wxuin=86107293996414; mm_lang=zh_CN; noticeLoginFlag=1; cert=9bBIg6HXL0ZvmwL9lmZAsF7eQEceSzfd; _clck=3928503461|1|fcr|0; uuid=8abd1b0f3452eb0a438757ba1726a0c2; bizuin=3928503461; ticket=6f090ad342a5ffc1312c3fde61ffc2352f48c030; ticket_id=gh_9b10aff30334; slave_bizuin=3928503461; rand_info=CAESIMV9caHy/7MNPw3a0GgAbHrFd0kBbAygbc/Vrmyx4KiC; data_bizuin=3928503461; data_ticket=Y9NEs5Nn52v8qyoKMhbKS8h6ARMu7E2PF7jhYpgmfQh98xkoGemhCtQBpj3sjSvC; slave_sid=UlpxSHJYVmpfcG9GMDNjRkNzZDI0Rm1YcVhRMFo4eGU2YUZTNF9JVHF2cnYzRUw1UTVnaGptRjNJMU5XMFpPSGpXYmZRbmNRQlZObElrZTI1R2lIQWtpU2pKd0dHc2VVbDdlZGxSaGtpQkhEU00wZVpXOWJjQXZLZ0c3OWwxQ0pERzNPRzIwaHBKdHVxSDJR; slave_user=gh_9b10aff30334; xid=9c3b8cb6836f39a19c8a5b7c36899b77; openid2ticket_opTQo6rYA33kqeYqkKRaa0BAPji4=YFxS4/EMPWyWgWABCQnbRAe8BjHejO4hvkvjfMZjS0w=; _clsk=1togqf9|1687655324343|7|1|mp.weixin.qq.com/weheat-agent/payload/record'
g_token = ''
g_cookies = {}
g_headers = {
    'accept': '*/*',
    'Referer': 'https://mp.weixin.qq.com/',
    'sec-ch-ua-platform': "Linux",
    'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Host': 'mp.weixin.qq.com'
}
c = {}


def load_cookies():
    import urllib
    global g_cookie_str, g_cookies
    prog = re.compile(r'\s?(?P<key>.*?)=(?P<val>.*)\s?')
    for item in g_cookie_str.split(';'):
        key, val = prog.match(item).groups()
        g_cookies[key] = val


url = 'http://mp.weixin.qq.com'


async def get_token():
    global g_headers, g_cookies
    print('c', c)
    async with aiohttp.ClientSession(cookies=c) as session:
        async with session.get(url=url) as resp:
            # print('resp.cookies', resp.cookies)
            print('aio: ', str(resp.url))
            if 200 == resp.status:
                token = re.findall(r'.*?token=(\d+)', str(resp.url))
                if token:
                    token = token[0]
                    return token
                else:
                    return


def get_token1():
    import requests
    global g_headers, g_cookies

    res = requests.Session().get(url=url,
                                 headers=g_headers,
                                 cookies=g_cookies,
                                 verify=True)
    print('requests: ', res.url)
    # print('request-cookies: ', res.cookies.items())

    # app_log.info(res.url)
    print(res.status_code)
    for k, v in res.cookies.items():
        c[k] = v


if __name__ == '__main__':
    load_cookies()
    get_token1()
    asyncio.run(get_token())