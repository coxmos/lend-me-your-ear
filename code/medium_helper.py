# -*- coding:utf-8 -*-
import json
from bs4 import BeautifulSoup


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
    with open('../data/honeypie.json', 'w') as f:
        f.write(json.dumps(res, ensure_ascii=False))


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
            data['page'] = str(post_info['url']).replace('medium.com', 'medium.xiaoyuu.ga').replace(
                'honeypie.wordpress.com', 'honeypie.xiaoyuu.ga')
        else:
            print(data['name'])

    with open('../data/data.json', 'w') as f:
        f.write(json.dumps(old_list, ensure_ascii=False))


if __name__ == '__main__':
    compare()
