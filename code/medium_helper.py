# -*- coding:utf-8 -*-
import json
from datetime import datetime

import threading
import os
import requests
from bs4 import BeautifulSoup


def read_urls():
    url_file = '../data/url.txt'
    with open(url_file) as f:
        raw_urls = f.readlines()
    urls = []
    [urls.append(url.strip()) for url in raw_urls]
    return urls


def do_task(url):
    # Todo 获取图片 日期 标题
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Version/13.1.1 Safari/605.1.15'}
    r = requests.get(url, headers=headers)
    return {
        'body': r.text,
        'url': r.url,
        'code': r.status_code
    }


"""
    <meta data-rh="true" property="article:published_time" content="2020-06-29T09:24:23.241Z"/>
    <meta data-rh="true" property="og:title" content="6/29 耳朵借我：李英宏談《水哥2020》"/>
    <meta data-rh="true" name="description"
          content="《水哥2020》原本可能會是《水哥2018》之類的，畢竟音樂大部分都在兩年前就做完了。若非一些不可抗拒的突發狀況，李英宏的第二張個人專輯並不會讓我們等四年，甚至在他以〈峇里島〉拿下金馬獎最佳原創電影歌曲之前，專輯或許就已經問世了。. “6/29 耳朵借我：李英宏談《水哥2020》” is published by 馬世芳 in 耳目江湖."/>
    <meta data-rh="true" property="og:image" content="https://miro.medium.com/max/1200/1*LeyLWxghj5ZlWK55kQg9qw.jpeg"/>
"""


def honey_pie_handle(html="xxx"):
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.find_all('div', {'class': "entrytitle"})
    for post in posts:
        title = post.find_all('a')[0].text
        link = post.find_all('a')[0]['href']
        print(title)
        print(link)


def handle_honeypie():
    with open('../data/medium/honeypie-list.txt') as f:
        lines = f.readlines()
    res = []
    for i in range(len(lines)):
        if i % 2 == 0:
            date, title = lines[i].strip().split(' ', 1)
            res.append({
                'title': title,
                'image': 'xxx',
                'date': date,
                'description': title,
                'url': lines[i + 1].strip()
            })
    with open('../data/honeypie.json','w') as f:
        f.write(json.dumps(res,ensure_ascii=False))

def handle_response(resp=None):
    if resp is None:
        return False
    if resp['code'] != 200:
        print(resp)
        return False
    soup = BeautifulSoup(resp['body'], 'html.parser')
    date_str = soup.find_all('meta', {'property': "article:published_time"})[0]['content']
    date = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
    date = date.strftime('%Y%m%d')

    title = soup.find_all('meta', {'property': "og:title"})[0]['content']
    image_url = soup.find_all('meta', {'property': "og:image"})[0]['content']

    description = soup.find_all('meta', {'name': "description"})[0]['content']
    url = resp['url']

    return {
        'title': title,
        'image': image_url,
        'date': date,
        'description': description,
        'url': url
    }


def download_image(date, url="https://xiaoyuu.ga/image.jpeg"):
    r = requests.get(url)
    image_dir = '/Users/xiaoyuu/lend-me-your-ear/image/'
    with open(image_dir + f'/{str(date)}.{url.rsplit(".")[-1]}', 'wb') as f:
        f.write(r.content)


def image_downloader():
    with open('../data/medium.json') as f:
        datalist = json.loads(f.read())
    cnt = 0
    for data in datalist:
        cnt += 1
        download_image(data['date'], data['image'])
        print(f"{data['date']}:{cnt}/{len(datalist)}")
    # thread_list = []
    # for i in range(20):
    #     thread = threading.Thread(target=)


def image_redownload():
    with open('../data/image.txt') as f:
        datalist = f.readlines()
    print(len(datalist))
    with open('../data/medium.json') as f:
        medium_list = json.loads(f.read())
    medium_dict = {}
    for medium in medium_list:
        medium_dict[medium['date']] = medium
    cnt = 0
    for data in datalist:
        cnt += 1
        date = data.split('/')[2].split('.')[0]
        medium = medium_dict.get(date)
        if medium is None:
            print("medium is None")
            continue

        print(f"{date}  {medium['title']}")


def image_check():
    image_dir = '../image'
    paths = os.listdir(image_dir)
    for path in paths:
        image_path = os.path.join(image_dir, path)
        size = os.path.getsize(image_path)
        if size == 64835:
            print(image_path)


def compare():
    old_list = []
    for year in [17, 18, 19, 20]:
        with open(f'../data/data_20{str(year)}.json') as f:
            old_list.extend(json.loads(f.read()))
    print(len(old_list))

    with open('../data/medium.json') as f:
        new_list = json.loads(f.read())

    same_cnt = 0
    # comp_list = []

    date_dict = {}
    for data in new_list:
        # comp_list.append(data['date'])
        date_dict[data['date']] = data


    for data in old_list:
        if data['date'] in date_dict.keys():
            post_info = date_dict.get(data['date'])
            data['content'] = post_info['description']
            if post_info['image'] == 'xxx':
                data['image'] = 'https://cdn.jsdelivr.net/gh/coxmos/lend-me-your-ear/avatar.png'
            else:
                data['image'] = f'https://cdn.jsdelivr.net/gh/coxmos/lend-me-your-ear/image/{post_info["date"]}.jpeg'
            data['page'] = str(post_info['url']).replace('medium.com','medium.xiaoyuu.ga').replace('honeypie.wordpress.com','honeypie.xiaoyuu.ga')
        else:
            print(data['name'])

    with open('../data/data.json','w') as f:
        f.write(json.dumps(old_list,ensure_ascii=False))


def get_infos():
    urls = read_urls()
    cnt = 0
    datalist = []
    for url in urls:
        cnt += 1
        print(f'{cnt} / {len(urls)}')
        resp = do_task(url)
        res = handle_response(resp)
        datalist.append(res)
        print(res)
    with open('../data/medium.json', 'w') as f:
        f.write(json.dumps(datalist, ensure_ascii=False))


if __name__ == '__main__':
    compare()