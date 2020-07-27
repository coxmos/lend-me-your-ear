import json
import xml.etree.ElementTree as ET


# def cdata(text):
#     res = '<![CDATA[' + text + ']]>'
#     return res

def rss_generator():
    rss_temp_file = '../rss/rss_template.xml'
    rss_file = '../rss/rss.xml'
    tree = ET.parse(rss_temp_file)
    rss = tree.getroot()
    channel = rss[0]

    items = get_items()
    print(len(items))
    for item in items:
        channel.append(item)
    tree.write(rss_file, 'UTF-8')


def get_items():
    item_list = []

    infolist = get_info_list()
    for info in infolist:
        item_list.append(getItem(info))
    return item_list


# < itunes: episodeType > full < / itunes: episodeType >
# < itunes: explicit > false < / itunes: explicit >
# < enclosure
# length = "92067632"
# type = "audio/mpeg"
# url = "https://one.xiaoyuu.ga/耳朵借我/2017/20170821%20他們的第一首歌（續）.mp3" / >
# < title > <![CDATA[20171212 hello送行]] > < / title >
# < description > 本集介绍及歌单查看请点击链接： < / description >
# < link > https: // ear.xiaoyuu.ga < / link >
# < guid > a9206763220171212 < / guid >
# < pubDate > Tue, 12
# Dec
# 2017
# 10: 00:00 - 0000 < / pubDate >
# < itunes: duration > 7303 < / itunes: duration >
# < / item >

# Todo 单集封面 单集网页 介绍单集网页 网页替换为 medium.xiaoyuu.ga https://honeypie.wordpress.com/page/2/?source=post_page-----c85918e998db----------------------
def get_info_list():
    json_file = '../data/data.json'
    res = []
    with open(json_file) as f:
        ep_list = json.loads(f.read())
    for ep in ep_list:
        info = {
            'image': ep['image'],
            'description': ep['content']+f"\n\n本集详细介绍以及歌单列表请查看网页:{ep['page']}",
            'link': ep['page'],

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


def test_duplication():
    """
    测试是否有重复日期
    :param year: 年份
    :return: None
    """
    date_set = set()
    info_list = get_info_list()
    for info in info_list:
        date_set.add(info['date'])
    print(len(info_list))
    print(len(date_set))


if __name__ == '__main__':
    rss_generator()
    # test_duplication()

