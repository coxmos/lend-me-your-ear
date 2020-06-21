import xml.etree.ElementTree as ET
import json

year_list = ['17', '18', '19', '20']


def rss_generator():
    rss_temp_file = '../rss/rss_template.xml'
    rss_file = '../rss/rss.xml'
    tree = ET.parse(rss_temp_file)
    rss = tree.getroot()
    channel = rss[0]

    for year in year_list:
        items = single_data_reader(year)
        print(len(items))
        for item in items:
            channel.append(item)
    tree.write(rss_file, 'UTF-8')


def single_data_reader(year):
    item_list = []

    infolist = get_info_list(year)
    for info in infolist:
        item_list.append(getItem(info))
    return item_list


def get_info_list(year):
    json_file = '../data/data_20' + year + '.json'
    res = []
    ep_list = []
    with open(json_file) as f:
        ep_list = json.loads(f.read())
    for ep in ep_list:
        info = {
            'image': 'https://lend-me-ears.github.io/image/avatar.png',
            'description': "暂无介绍，后期会补上，敬请谅解。",
            'link': 'https://lend-me-ears.github.io',

            'length': str(ep['size']),
            'file': ep['url'],
            'title': ep['name'],
            'guid': ep['guid'],
            'date': ep['timestamp'],
            'duration': str(ep['duration'])
        }
        res.append(info)
    return res


def getItem(info):
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
    enclosure = ET.SubElement(item, 'enclosure', {'length': info['length'], 'type': 'audio/mpeg', 'url': info['file']})

    title = ET.SubElement(item, 'title')
    title.text = info['title']
    description = ET.SubElement(item, 'description')
    description.text = info['description']
    link = ET.SubElement(item, 'link')
    link.text = info['link']
    guid = ET.SubElement(item, 'guid')
    guid.text = info['guid']
    pubDate = ET.SubElement(item, 'pubDate')
    pubDate.text = info['date']
    duration = ET.SubElement(item, 'itunes:duration')
    duration.text = info['duration']

    return item


def test_duplication(year):
    """
    测试是否有重复日期
    :param year: 年份
    :return: None
    """
    date_set = set()
    info_list = get_info_list(year)
    for info in info_list:
        date_set.add(info['date'])
    print(len(date_set))


if __name__ == '__main__':
    rss_generator()
    # for year in year_list:
    #     test_duplication(year)
