# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from .utils import write_file
import math
import random


def parse_wexin_article(html_text):
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
    
def link_sogou_analysis(href: str):
    b = math.floor(random.random()  * 100 + 1)
    a = href.index('url=')
    a = href[a + 4 + 21 + b]
    link = f'{href}&k={b}&h={a}'
    return f'https://weixin.sogou.com/{link}'
    
# def get_sogou_link(href: str):
#     pass


def parse_sougou_pages(html_text) -> list:
    try:
        soup = BeautifulSoup(html_text, 'lxml')
        li_list = soup.find('ul', class_='news-list').find_all('li')
        res = []
        for li in li_list:
            cover = 'https:' + li.find('img').get('src')
            title = li.select_one('.txt-box>h3>a').text
            update_time = li.find('div', class_='s-p').get('t')
            extracted_from = li.select_one('.s-p>.account').text
            href = li.select_one('.txt-box>h3>a').get('href')
            href = link_sogou_analysis(href)
            # link = get_sogou_link(href)
            res.append({
                'cover': cover,
                'title': title,
                'update_time': int(update_time),
                'extracted_from': extracted_from,
                'link': href,
            })
        return res
    except Exception as e:
        print(e)
        print(html_text)



def parse_wexin_article_(html_text):
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
    parse_wexin_article_('')




