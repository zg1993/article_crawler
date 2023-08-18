# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from .utils import write_file, str_to_timestamp, app_log
import math
import random
from datetime import datetime
import re


def parse_wexin_article(html_text):
    try:
        soup = BeautifulSoup(html_text, 'lxml')
        title = soup.find(property='og:title')
        url1 = soup.find(property='og:url')
        des = soup.find(property='og:description')
        img = soup.find(property='og:image')
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
    b = math.floor(random.random() * 100 + 1)
    a = href.index('url=')
    a = href[a + 4 + 21 + b]
    link = f'{href}&k={b}&h={a}'
    return f'https://weixin.sogou.com/{link}'


# def get_sogou_link(href: str):
#     pass


def parse_toutian_article(html_text):
    try:

        soup = BeautifulSoup(html_text, 'lxml')
        link_element = soup.find('link', rel='canonical')
        link = ''
        aid = ''
        if link_element:
            link = link_element.get('href')
            aid = link.split('/')[-2]
        article_content = soup.find('div', class_='article-content')
        pgc_imgs = article_content.find_all('div', class_='pgc-img')
        for pgc_img in pgc_imgs:
            pass
            # pgc_img['style'] = 'text-align: center'
        imgs = article_content.find_all('img')
        for img in imgs:
            img['referrerPolicy'] = 'same-origin'
        title = article_content.find('h1').text
        artilce_meta_list = article_content.select_one(
            '.article-meta').find_all('span')
        for span in artilce_meta_list:
            if not span.get('class'):
                date_str = span.text
                update_time = str_to_timestamp(date_str, '%Y-%m-%d %H:%M')
                break
        extracted_from = article_content.select_one('.article-meta>.name').text
        content_element = article_content.find('article',
                                               class_='tt-article-content')
        content = content_element.prettify()
        return {
            'update_time': update_time,
            'content': content,
            'extracted_from': extracted_from,
            'title': title,
            'link': link,
            'aid': aid
        }
    except Exception as e:
        app_log.error(e)
        print(html_text)


def parse_toutian_pages(html_text) -> list:
    try:
        soup = BeautifulSoup(html_text, 'lxml')
        res = []
        li_list = soup.find('div', class_='s-result-list').find_all(
            'div', class_='result-content')
        app_log.info(len(li_list))
        for li in li_list:
            app_log.info(li)
            if li.get('data-i') is not None:
                # app_log.info(li)
                title_element = li.find(
                    'div',
                    class_=
                    'flex-1 text-darker text-xl text-medium d-flex align-items-center overflow-hidden'
                ).find('a')
                img_element = li.find('img')
                if title_element and img_element:
                    cover = img_element.get('src')
                    title = title_element.text
                    link = 'https://so.toutiao.com' + title_element.get('href')
                    res.append({'link': link, 'title': title, 'cover': cover})
        # app_log.info(res)
        return res
    except Exception as e:
        app_log.error(e)
        print(html_text)
        return []


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


def parse_carbon_market_gz(html_text, marketSegment, **kwargs):
    try:
        res = []
        soup = BeautifulSoup(html_text, 'lxml')
        trs = soup.select_one('table[id="mytable"]').find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')
            # print(tds)
            [
                nowDate, _, openPrice, closePrice, hightPrice, lowPrice,
                riseAndFall, chg, turnover, transactionAmount
            ] = [re.compile(r'\s').sub('', td.text) for td in tds]
            # print(type(nowDate))
            nowDate = datetime.strptime(nowDate, '%Y%m%d').strftime('%Y-%m-%d %H:%M:%S')
            # print(nowDate)
            element = {
                'nowDate': nowDate,
                'openPrice': float(openPrice),
                'closePrice': float(closePrice),
                'hightPrice': float(hightPrice),
                'lowPrice': float(lowPrice),
                'chg': float(chg.strip('%')),
                'turnover': float(turnover),
                'transactionAmount': float(transactionAmount),
                'riseAndFall': float(riseAndFall),
                "marketSegment": marketSegment
            }
            return element

    except Exception as e:
        app_log.info(e)


def parse_carbon_market_hb(html_text, marketSegment, **kwargs):
    try:
        res = []
        soup = BeautifulSoup(html_text, 'lxml')
        uls = soup.find('div', class_='future_table').find_all('ul',
                                                               class_='cont')
        if datetime.now().strftime('%H:%M') > "17:00":
            ul = uls[0]
        else:
            ul = uls[1]
        lis = ul.find_all('li')
        [
            _, nowDate, closePrice, chg, hightPrice, lowPrice, turnover,
            transactionAmount, openPrice
        ] = [re.compile(r'\s').sub('', li.text) for li in lis]
        chg = float(chg.strip('%'))
        riseAndFall = round((float(closePrice) * chg) / (100 + chg), 2)
        element = {
            'nowDate': f'{nowDate} 00:00:00',
            'openPrice': float(openPrice),
            'closePrice': float(closePrice),
            'hightPrice': float(hightPrice),
            'lowPrice': float(lowPrice),
            'chg': chg,
            'turnover': float(turnover),
            'transactionAmount': float(transactionAmount),
            'riseAndFall': float(riseAndFall),
            "marketSegment": marketSegment
        }

        return element
    except Exception as e:
        app_log.info(e)

def parse_carbon_market_sz(response, marketSegment, **kwargs):
    # 深圳没有涨跌幅度，成交均价等于收盘价格
    try:
        res = []
        content_arr = response['data']['content']
        content_arr = list(filter(lambda i: i['title'].endswith('SZEA'), content_arr))
        data, last_data = content_arr[:2]
        riseAndFall = round(float(data['dailyClosingPrice']) - float(last_data['dailyClosingPrice']), 2)
        chg = (riseAndFall / float(last_data['dailyClosingPrice'])) * 100
        element = {
            'nowDate': data['tradeDate'],
            'openPrice': float(data['dailyOpeningPrice']),
            'closePrice': float(data['dailyClosingPrice']),
            'hightPrice': float(data['dailyHighestPrice']),
            'lowPrice': float(data['dailyLowestPrice']),
            'chg': round(chg, 2),
            'turnover': float(data['sumAmount']),
            'transactionAmount': float(data['sumPrice']),
            'riseAndFall': riseAndFall,
            "marketSegment": marketSegment
        }

        return element
    except Exception as e:
        app_log.info(e)

def parse_carbon_market_bj(html_text, marketSegment, **kwargs):
    try:
        res = []
        soup = BeautifulSoup(html_text, 'lxml')
        trs = soup.find('table').find_all('tr')
        today = [td.text.strip() for td in trs[1].find_all('td')]
        yesterday = [td.text.strip() for td in trs[2].find_all('td')]
        print(today)
        print(yesterday)
        nowDate, turnover, average_price, transactionAmount = today
        last_average_price = float(yesterday[2])
        turnover = float(turnover)
        average_price = float(average_price)
        transactionAmount = float(transactionAmount.replace(',', '')[:-6])
        print(last_average_price)
        print(nowDate)
        print(turnover)
        print(average_price)
        print(transactionAmount)
        closePrice = openPrice = hightPrice = lowPrice = average_price
        riseAndFall = round(average_price - last_average_price, 2)
        chg = (riseAndFall / last_average_price) * 100
        element = {
            'nowDate': f'{nowDate} 00:00:00',
            'openPrice': openPrice,
            'closePrice': closePrice,
            'hightPrice': hightPrice,
            'lowPrice': lowPrice,
            'chg': round(chg, 2),
            'turnover': turnover,
            'transactionAmount': transactionAmount,
            'riseAndFall': riseAndFall,
            "marketSegment": marketSegment
        }
        return element
    except Exception as e:
        app_log.info(e)


def parse_carbon_market(html_text, marketSegment):
    try:
        res = []
        soup = BeautifulSoup(html_text, 'lxml')
        articles = soup.find_all('article', class_='blog-single-wrap mb-40')
        for article in articles:
            title = article.find('h3', class_='blog-wrap-title')
            if '碳行情' in title.text:
                table = article.find('table',
                                     class_='table table-hover text-center')
                tds = table.find('tbody').find('tr').find_all('td')
                # trs = table.find('tbody').find_all('tr')
                # for tr in trs:
                # tds = tr.find_all('td')
                nowDate, openPrice, closePrice, hightPrice, lowPrice, chg, turnover, transactionAmount, _ = [
                    td.text.replace(',', '') for td in tds
                ]
                nowDate = f'{nowDate} 00:00:00'
                openPrice = float(openPrice)
                closePrice = float(closePrice)
                hightPrice = float(hightPrice)
                lowPrice = float(lowPrice)
                chg = float(chg.strip('%'))
                turnover = float(turnover)
                transactionAmount = float(transactionAmount)
                chg_value = chg
                riseAndFall = round(
                    (closePrice * chg_value) / (100 + chg_value), 2)
                # print(nowDate, openPrice, closePrice, hightPrice, lowPrice,
                #   chg, turnover, transactionAmount, riseAndFall)
                element = {
                    'nowDate': nowDate,
                    'openPrice': openPrice,
                    'closePrice': closePrice,
                    'hightPrice': hightPrice,
                    'lowPrice': lowPrice,
                    'chg': chg,
                    'turnover': turnover,
                    'transactionAmount': transactionAmount,
                    'riseAndFall': riseAndFall,
                    "marketSegment": marketSegment
                }
                return element
                # return res
    except Exception as e:
        app_log.info(e)


def parse_wexin_article_(html_text):
    # url = 'https://mp.weixin.qq.com/s?__biz=MjM5OTU4Nzc0Mg==&mid=2658853306&idx=1&sn=f39bb57ae7e368be93b73ec06755c967&chksm=bcb77b4b8bc0f25d8e2bc06f0c5119bffef4d2e48ba28a74f467dc3abf79cd265c2da5f0a900&token=1327459081&lang=zh_CN#rd'
    url = 'https://mp.weixin.qq.com/s?__biz=MzAwODk0NzU4OA==&mid=2247521644&idx=1&sn=9c1a9c735f2fdd05c127fc63b81104da&chksm=9b65c787ac124e9129c6089609d34a3e27a3178147ee58253617c7c92684905fea33aca075b8#rd'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'lxml')
    title = soup.find(property='og:title')
    url1 = soup.find(property='og:url')
    des = soup.find(property='og:description')
    img = soup.find(property='og:image')
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
