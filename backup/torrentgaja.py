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
HOST = "https://torrentgaja.com"
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
    class_word = 'list-group-item en font-14 break-word'
    magnet = soup.find('li', {'class': class_word}).text.strip()
    return magnet


@debug
def print_torrent_table():
    keyword = input("input the keyword: ")
    all_data = []
    url = ('https://torrentgaja.com/bbs/search.php?'\
          'search_flag=search&stx={}').format(keyword)
    soup = get_soup(url)
    titles = [x for x in soup.find_all(
              "span", {"class": "text-muted"})][1::2]
    titles = [all_data.append([x.text]) for x in titles]
    bbs_urls = []
    for div in soup.find_all("div", {"class": "media-heading"}):
        bbs_url = urljoin(url, div.find("a", href=True)['href'])
        bbs_urls.append(bbs_url)
    if len(bbs_urls) == 0:
        print("======== Couldn't find any torrents =========")
        return
    jobs = [gevent.spawn(get_magnet_link, url) for url in bbs_urls]
    gevent.joinall(jobs)
    magnet_urls = [job.value for job in jobs]
    for n, d in enumerate(all_data, 0):
        d.append(magnet_urls[n])
        d.insert(0, n+1)
    all_data.insert(0, ['No', 'Title', 'Magnet'])
    table = AsciiTable(all_data)
    for n in range(len(all_data)):
        table.justify_columns[n] = 'center'
    print(table.table)


if __name__ == '__main__':
    print_torrent_table()
