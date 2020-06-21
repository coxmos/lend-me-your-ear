import json
from email import utils
import time
from datetime import datetime
import os
from mutagen.mp3 import MP3


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


def get_information(path, year):
    """
    爬取文件列表数据
    :param path: 文件夹
    :param year: 年份
    :return: None
    """
    res = []

    base_url = 'https://cloud.lend-me-ears.workers.dev/0:'
    filelist = os.listdir(path)
    for file in filelist:
        if file.find('.mp3') < 0:  # 跳过非音频文件
            continue
        filepath = os.path.join(path, file)
        size = os.path.getsize(filepath)
        url = base_url + '/' + year + '/' + file
        date = file.split(' ')[0]
        timestamp = get_timestamp(date)
        name = file.rsplit('.', 1)[0]
        guid = 'a' + str(size) + str(date)
        duration = int(MP3(filepath).info.length)
        res.append({
            'name': name,
            'url': url,
            'duration': duration,
            'size': size,
            'date': date,
            'timestamp': timestamp,
            'guid': guid
        })

    with open('../data/data_' + year + '.json', 'w') as f:
        f.write(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    get_information('/Users/zhangxiaoyu/Downloads/耳朵借我/2018', '2018')
