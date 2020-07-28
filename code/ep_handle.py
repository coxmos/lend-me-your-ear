import os
import time
from datetime import datetime
from email import utils

import requests
from bs4 import BeautifulSoup
from mutagen.mp3 import MP3
from urllib import parse
import xml.etree.ElementTree as ET


def get_timestamp(date):
    """
    得到 rfc2822 时间戳
    :param date: 日期 格式：20200222
    :return: 时间戳
    """
    date_time = datetime.strptime(date, '%Y%m%d').replace(hour=18)
    date_tuple = date_time.timetuple()
    date_timestamp = time.mktime(date_tuple)
    res = utils.formatdate(date_timestamp)
    return res


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


def download_image(base_url, date, url="https://xiaoyuu.ga/image.jpeg"):
    r = requests.get(url)
    with open(base_url + f'/{str(date)}.jpeg', 'wb') as f:
        # if len(r.content) ==
        f.write(r.content)


def single_file_handle(medium_url, base_path, filename):
    if filename.count('.mp3') != 1:
        print(filename)
        return
    base_audio_url = 'https://drive.xiaoyuu.ga/0:'

    filepath = os.path.join(base_path, filename)

    date = filename.split(' ', 1)[0]
    year = date[:4]

    duration = int(MP3(filepath).info.length)
    name = filename.rsplit('.', 1)[0]
    size = os.path.getsize(filepath)
    url = base_audio_url + '/' + year + '/' + parse.quote(filename)
    guid = 'a' + str(size) + str(date)
    timestamp = get_timestamp(date)

    resp = handle_response(do_task(medium_url))
    page = medium_url.replace('medium.com', 'medium.xiaoyuu.ga').replace('honeypie.wordpress.com',
                                                                         'honeypie.xiaoyuu.ga')
    download_image(base_path, date, resp['image'])
    return {
        'name': name,
        'url': url,
        'duration': str(duration),
        'size': str(size),
        'date': date,
        'timestamp': timestamp,
        'guid': guid,
        'content': resp['description'] + f"\n\n本集详细介绍及歌单列表,请查看网页:{page}",
        'image': f'https://cdn.jsdelivr.net/gh/coxmos/lend-me-your-ear/image/{date}.jpeg',
        'page': page,
    }


"""
  {
"name": "20170815 他們的第一首歌",
"url": "https://drive.xiaoyuu.ga/0:/2017/20170815 他們的第一首歌.mp3",
"duration": 7236,
"size": 93048496,
"date": "20170815",
"timestamp": "Tue, 15 Aug 2017 10:00:00 -0000",
"guid": "a9304849620170815",
"content": "他們的第一首歌",
"image": "https://cdn.jsdelivr.net/gh/coxmos/lend-me-your-ear/avatar.png",
"page": "https://honeypie.xiaoyuu.ga/2017/08/14/8-15-fm96-3%e3%80%8c%e8%80%b3%e6%9c%b5%e5%80%9f%e6%88%91%e3%80%8d%ef%bc%9a%e4%bb%96%e5%80%91%e7%9a%84%e7%ac%ac%e4%b8%80%e9%a6%96%e6%ad%8c/"
},
"""


def rss_generator(base_url, infos):
    rss_file = os.path.join(base_url, 'rss.xml')
    root = ET.Element('root')

    for info in infos:
        item = get_item(info)
        root.append(item)
    tree = ET.ElementTree(root)
    tree.write(rss_file, 'UTF-8')


def get_item(info):
    """
    添加单集信息
    :param info: 单集信息
    :return: Element
    """
    item = ET.Element('item')

    episodeType = ET.SubElement(item, 'itunes:episodeType')
    episodeType.text = 'full'
    explicit = ET.SubElement(item, 'itunes:explicit')
    explicit.text = 'false'

    image = ET.SubElement(item, 'itunes:image', {'href': info['image']})
    enclosure = ET.SubElement(item, 'enclosure', {'length': str(info['size']), 'type': 'audio/mpeg', 'url': info['url']})

    title = ET.SubElement(item, 'title')
    title.text = info['name']
    description = ET.SubElement(item, 'description')
    description.text = info['content']
    link = ET.SubElement(item, 'link')
    link.text = info['page']
    guid = ET.SubElement(item, 'guid')
    guid.text = info['guid']
    pubDate = ET.SubElement(item, 'pubDate')
    pubDate.text = info['timestamp']
    duration = ET.SubElement(item, 'itunes:duration')
    duration.text = str(info['duration'])

    return item


def handle_file():
    base_path = '../../Downloads/ear'
    files = os.listdir(base_path)
    infos = []
    for file in files:
        print('\n' + file)
        medium_url = input(f'输入medium链接：\n')
        res = single_file_handle(medium_url, base_path, file)
        if res is not None:
            infos.append(res)
            print(res)
    rss_generator(base_path, infos)



if __name__ == '__main__':
    handle_file()
    # rss_generator('../../Downloads/ear',infos)
