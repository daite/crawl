#!/usr/bin/env python3

from terminaltables import AsciiTable
from bs4 import BeautifulSoup as BS
from urllib.parse import urljoin
from collections import deque
from functools import wraps
from gevent import monkey
import gevent
import re
monkey.patch_all()
import requests

pat = re.compile('[A-Z0-9]+')
HOST = "https://torrenthaja.com"
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
def get_soup(url):
    soup = BS(requests.get(url, headers=headers).content, 'lxml')
    return soup

@debug
def get_magnet_link(bbs_url):
    soup = get_soup(bbs_url)
    magnet_prefix = 'magnet:?xt=urn:btih:'
    try:
        magnet = soup.find('button', onclick=True)['onclick']
        magnet = re.search(pat, magnet).group()
        magnet = magnet_prefix + magnet
    except:
        magnet = "couldn't get magnet data"
    return magnet


@debug
def print_torrent_table():
    keyword = input("input the keyword: ")
    all_data = []
    url = ('https://torrenthaja.com/bbs/search.php?'\
          'search_flag=search&stx={}').format(keyword)
    soup = get_soup(url)
    for tr in soup.find_all('tr'):
        data = [x.text.strip()[:40] for x in tr.find_all('td')] 
        d = deque(data)
        d.rotate()
        all_data.append(list(d))
    table_data = all_data[1:]

    bbs_urls = [urljoin(urljoin(HOST, 'bbs/'), x.find('a')['href']) 
                for x in soup.find_all('div', {'class': 'td-subject ellipsis'})] 
    if len(bbs_urls) == 0:
        print("======== Couldn't find any torrents =========")
        return
    jobs = [gevent.spawn(get_magnet_link, url) for url in bbs_urls]
    gevent.joinall(jobs)
    magnet_urls = [job.value for job in jobs]

    for n, d in enumerate(table_data):
        d.append(magnet_urls[n])
    table_data.insert(0, ['Date', 'Category', 'Title', 'File Size', 'Magnet'])
    table = AsciiTable(table_data)
    for n in range(len(table_data)):
        table.justify_columns[n] = 'center'
    print(table.table)


if __name__ == '__main__':
    print_torrent_table()
