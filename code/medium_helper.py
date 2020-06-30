# -*- coding:utf-8 -*-
import json
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def read_urls():
    url_file = '../data/url.txt'
    with open(url_file) as f:
        raw_urls = f.readlines()
    urls = set()
    for url in raw_urls:
        url = url.split('?')[0]
        urls.add(url)
    return urls


def cleanup(soup):
    invalid_tags = ['div', 'span', 'noscript']
    invalid_attributes = ['class', 'id', 'rel']
    delete_tags = ['h1', 'button']

    for tag in invalid_tags:
        for match in soup.findAll(tag):
            match.replaceWithChildren()
    for attribute in invalid_attributes:
        for tag in soup.find_all(attrs={attribute: True}):
            del tag[attribute]
    for tag in delete_tags:
        for match in soup.findAll(tag):
            match.extract()

    for a_tag in soup.find_all('a', attrs={'target': False}):
        a_tag.extract()

    for img_tag in soup.find_all('img', attrs={'src': False}):
        img_tag.replaceWithChildren()

    for img_tag in soup.find_all('img', attrs={'src': True}):
        if str(img_tag['src']).count('q=20') > 0:
            img_tag.replaceWithChildren()

    return soup


def get_post(html):
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15'}
    # response = requests.get(link,headers = headers)
    soup = BeautifulSoup(html, 'html.parser')
    date = soup.find_all('meta', {'property': "article:published_time"})[0]['content']
    date = date.split('T')[0]
    date = datetime.strptime(date, '%Y-%m-%d')
    date = date.strftime('%Y%m%d')

    title = soup.find_all('h1')[0].get_text()

    content = cleanup(soup.find_all('div', {'class': 'z ab ac ae af du ah ai'})[0])

    imgs = content.find_all('img', {'src': True})
    images = set()
    for img in imgs:
        images.add(img['src'])
    return {
        'title': str(title),
        'date': date,
        'images': list(images),
        'content': str(content)
    }


def download_images(date, urls):
    cnt = 0
    for url in urls:
        cnt += 1
        r = requests.get(url)
        image_dir = '/Users/zhangxiaoyu/lend-me-ears.github.io/image/{}'.format(date)
        if not os.path.exists(image_dir):
            os.mkdir(image_dir)
        with open(image_dir + '/{}.jpeg'.format(cnt), 'wb') as f:
            f.write(r.content)


def image_downloader():
    with open('../data/medium/medium.json') as f:
        datalist = json.loads(f.read())
        print(len(datalist))
    for data in datalist:
        download_images(data['date'], data['images'])
        print(data['date'], 'finish..')


def generate_medium_json():
    # urls = read_urls()
    res = []
    htmls = os.listdir('../data/medium')
    for html in htmls:
        with open('../data/medium/' + html) as f:
            res.append(get_post(f.read()))
    with open('../data/medium_new.json', 'w') as f:
        f.write(json.dumps(res, ensure_ascii=False))


def main():
    with open('../data/medium.json') as f:
        datalist = json.loads(f.read())

    audio_list = []
    for year in ['17', '18', '19', '20']:
        with open('../data/data_20' + year + '.json') as f:
            audio_list.extend(json.loads(f.read()))

    samecnt = 0
    no_medium_date_list = []
    data_list = []
    for data in datalist:
        data_list.append(data['date'])
    for audio in audio_list:

        if audio['date'] in data_list:
            samecnt += 1
        else:
            no_medium_date_list.append(audio['date'])
    print()
    print(samecnt)
    print()
    print(no_medium_date_list)
    print(len(no_medium_date_list))

    # with open('../data/medium.json', 'w') as f:
    #     f.write(json.dumps(datalist, ensure_ascii=False))


if __name__ == '__main__':
    # main()
    # 105 105 40 49
    # generate_medium_json()
    image_downloader()
    # date = datetime.strptime(date, '%Y/%m/%d')
    # date = date.strftime('%Y%m%d')
    # print(date)
