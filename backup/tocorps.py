#!/usr/bin/env python3

from terminaltables import AsciiTable
from bs4 import BeautifulSoup as BS
from urllib.parse import urlencode
from functools import wraps
from gevent import monkey
import gevent
monkey.patch_all()
import requests

param = {
    'key': 'AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY',
    'cse_tok':'ABPF6HiCHIVJrxlXCDeQ_MhDTTgcCDw83g:1529916884758',
    'sig': '4aa0772189af4c17ea7ec181af2bca15',
    'cx': '008614474937839428461:i55eqojmyye',
    'rsz': 'filtered_cse',
    'num': '20',
    'hl': 'ko',
    'prettyPrint': 'true',
    'source': 'gcsc',
    'gss': '.com',
    'q': '',
}

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('[*]Running from {} ....'.format(func.__name__))
        return func(*args, **kwargs)
    return wrapper


@debug
def get_magnet(bbs_url):
    soup = BS(requests.get(bbs_url, headers=headers).content, 'lxml')
    for s in soup.find_all('a', href=True):
        text = s['href']
        if text.startswith('magnet'):
            return text


@debug
def print_torrent_table():
    keyword = input('input the keyword: ')
    param['q'] = keyword
    all_data = []
    bbs = []
    base_url = 'https://www.googleapis.com/customsearch/v1element'
    url = '{}?{}'.format(base_url, urlencode(param))
    r = requests.get(url, headers=headers)
    results = r.json()['results']
    for n, result in enumerate(results, 1):
        mdata = result['richSnippet']['metatags']
        description = mdata['ogDescription'].split('용량:')
        title = mdata['ogTitle'][:40]
        file_size = description[-1].strip()
        bbs_link = mdata['ogUrl'].replace('/m/bbs/', '/bbs/')
        bbs.append(bbs_link)
        all_data.append([n, title, file_size])

    jobs = [gevent.spawn(get_magnet, bbs_url) for bbs_url in bbs]
    gevent.joinall(jobs)
    magnet_urls = [job.value for job in jobs]
    
    for n, d in enumerate(all_data):
        d.append(magnet_urls[n])

    all_data.insert(0, ['No', 'Title', 'File size', 'Magnet'])
    table = AsciiTable(all_data)
    for n in range(len(all_data)):
        table.justify_columns[n] = 'center'
    print(table.table)


if __name__ == '__main__':
    print_torrent_table()
