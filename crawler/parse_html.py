# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from tools.utils import write_file


def parese_wexin_article(html_text):
    try:
        soup = BeautifulSoup(html_text, 'lxml')
        title = soup.find(property='og:title')
        url1 = soup.find(property='og:url')
        des = soup.find(property='og:description')
        img =  soup.find(property='og:image')
        body = soup.find(id='activity-detail')
        content = body.find(id='js_content')
        if not content:
            content = body.find(id='js_article_content')
        # print(content.prettify())
        imgs = content.find_all('img')
        for img in imgs:
            img_url = img.get('data-src')
            if img_url:
                img['src'] = img_url
                img['referrerPolicy'] = 'same-origin'
        # 判断content只有一个div标签
        if len(content.find_all('div')):
            print('parse {} error'.format(title))
        else:
            content.name = 'p'
        return content.prettify()
    except Exception as e:
        print(e)
        return None

def parese_wexin_article_(html_text):
    # url = 'https://mp.weixin.qq.com/s?__biz=MjM5OTU4Nzc0Mg==&mid=2658853306&idx=1&sn=f39bb57ae7e368be93b73ec06755c967&chksm=bcb77b4b8bc0f25d8e2bc06f0c5119bffef4d2e48ba28a74f467dc3abf79cd265c2da5f0a900&token=1327459081&lang=zh_CN#rd'
    url = 'https://mp.weixin.qq.com/s?__biz=MzAwODk0NzU4OA==&mid=2247521644&idx=1&sn=9c1a9c735f2fdd05c127fc63b81104da&chksm=9b65c787ac124e9129c6089609d34a3e27a3178147ee58253617c7c92684905fea33aca075b8#rd'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    title = soup.find(property='og:title')
    url1 = soup.find(property='og:url')
    des = soup.find(property='og:description')
    img =  soup.find(property='og:image')
    # print(url1.get('content')==url)
    # print(url1.get('content'))
    # print('img: ', img) # 列表里显示的图片
    # print('title: ', title)
    # print('url1: ', url1.contents) # url
    # print('des: ', des)
    body = soup.find(id='js_article')
    title_tag = soup.find(id='activity-name')
    content = body.find(id='js_content')
    print(content)
    if not content:
        content = body.find(id='js_article_content')
    # print(content.prettify())
    imgs = content.find_all('img')
    for img in imgs:
        img_url = img.get('data-src')
        if img_url:
            img['src'] = img_url
            img['referrerPolicy'] = 'same-origin'
    # 判断content只有一个div标签
    if len(content.find_all('div')):
        print('parse {} error'.format(title))
    else:
        content.name = 'p'
    # print(content.prettify())
    path = '/home/zg/work/PIC/{}.html'.format('1')
    write_file(path, content.prettify())
    


if __name__ == '__main__':
    parese_wexin_article_('')




