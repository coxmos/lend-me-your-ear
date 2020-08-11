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


def download_image(date, url="https://xiaoyuu.ga/image.jpeg"):
    r = requests.get(url)
    with open(f'../image/{str(date)}.jpeg', 'wb') as f:
        f.write(r.content)


def handle_file(base_path, filename):
    if filename.count('.mp3') != 1:
        print(filename)
        return None
    base_audio_url = 'https://one.xiaoyuu.ga/耳朵借我'
    filepath = os.path.join(base_path, filename)
    date = filename.split(' ', 2)[1]
    year = date[:4]
    name = filename.split(' ', 2)[2].rsplit('.', 1)[0]
    size = os.path.getsize(filepath)
    url = f'{base_audio_url}/{year}/{parse.quote(filename)}'
    guid = 'a' + str(size) + str(date)
    timestamp = get_timestamp(date)
    image = ''
    has_image = input('有單集圖片嗎（no-0，yes-1）：')
    if has_image == '1':
        image = f'https://cdn.jsdelivr.net/gh/coxmos/lend-me-your-ear/image/{date}.jpeg'
    link = input('請輸入單集網址：（如沒有請按回車）').strip()
    link = link.replace('medium.com', 'medium.xiaoyuu.ga').replace('honeypie.wordpress.com', 'honeypie.xiaoyuu.ga')
    description = '<![CDATA['
    text = read_description().strip()
    if text != '':
        description += text
    if link != '':
        resp = handle_response(do_task(link))
        download_image(date, resp['image'])
        description += f'<p></p><p>本集详细介绍及歌单列表,请查看网页：<a href="{link}">點我</a></p>'
    description += f'<p></p><p>把耳朵借給馬世芳吧，电台节目「耳朵借我」非官方存档。</p> 如有問題或者建議，请在<a href="https://ear.xiaoyuu.ga">ear.xiaoyuu.ga</a>底部留言，或者发邮件至 <a href="mailto:ear@xiaoyuu.ga">ear@xiaoyuu.ga</a>。</p>]]>'

    return {
        'title': name,
        'url': url,
        'length': str(size),
        'season': year,
        'pubDate': timestamp,
        'guid': guid,
        'description': description,
        'image': image,
        'link': link,
    }


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
    if info['image'].strip() != '':
        image = ET.SubElement(item, 'itunes:image', {'href': info['image']})
    if info['link'].strip() != '':
        link = ET.SubElement(item, 'link')
        link.text = info['link']

    enclosure = ET.SubElement(item, 'enclosure',
                              {'length': str(info['length']), 'type': 'audio/mpeg', 'url': info['url']})
    title = ET.SubElement(item, 'title')
    title.text = info['title']
    description = ET.SubElement(item, 'description')
    description.text = info['description']
    guid = ET.SubElement(item, 'guid')
    guid.text = info['guid']
    pubDate = ET.SubElement(item, 'pubDate')
    pubDate.text = info['pubDate']
    season = ET.SubElement(item, 'season')
    season.text = str(info['season'])

    return item


def main():
    base_path = '../../Downloads/ear'
    files = os.listdir(base_path)
    infos = []
    for file in files:
        print('\n' + file)
        res = handle_file(base_path, file)
        if res is not None:
            infos.append(res)
        else:
            print(f"Error:{file}")
    rss_generator(base_path, infos)


def add_p_label(lines=[]):
    text = ''
    for line in lines:
        text += f'<p>{line}</p>'
    return text


def read_description():
    lines = []
    line = input("請輸入介紹：（默認請回車, q 退出):")
    while line != 'q':
        lines.append(line)
        line = input()
    return add_p_label(lines)


if __name__ == '__main__':
    # main()

    print(read_description())