#!/usr/bin/env python3

from terminaltables import AsciiTable
from bs4 import BeautifulSoup as BS
from urllib.parse import urljoin, quote_plus
from functools import wraps
from gevent import monkey
import gevent
import sys
monkey.patch_all()
import requests

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("[+] Executing {} ...." .format(func.__name__))
        return func(*args, **kwargs)
    return wrapper


@debug
def get_info(session, num, board_url):
        r = session.get(board_url, headers=headers)
        soup = BS(r.content, 'lxml')
        title = soup.find('h1')['content']
        try:
            magnet = soup.find('ul', {'class': 'list-group'}).text.strip()
        except AttributeError:
            magnet = 'No magnet data'
        return num, title, magnet[:60]


@debug
def print_torrent_table():

    keyword = input("input the keyword: ")
    password = input("input the password: ")
    login_url = 'https://torrentluv.net/bbs/login_check.php'
    with requests.Session() as s:
        data = {
        'mb_id': 'ddalddalyi', 
        'mb_password': password,
        }
        r = s.post(login_url, headers=headers, data=data)
        if r.text.find(data['mb_password']) != -1:
            print("[+] Login Success!")
        else:
            print("[-] Login Fail!")
            sys.exit(1)

        search_url = ('https://torrentluv.net/bbs/search.php?stx={}').\
                      format(quote_plus(keyword))
        r = s.get(search_url, headers=headers)
        soup = BS(r.content, 'lxml')
        links = []
        for div in soup.find_all('div', {'class': 'media-body'}):
            link = div.find('a', href=True)['href']
            board_url = urljoin(login_url, link)
            links.append(board_url)

        jobs = [gevent.spawn(get_info, s, n, link) \
                for n, link in enumerate(links, 1)]
        gevent.joinall(jobs, timeout=10)
        data = [job.value for job in jobs]

        data.insert(0, ['No', 'Title', 'Magnet'])
        table = AsciiTable(data)
        for n in range(len(data)):
            table.justify_columns[n] = 'center'
        print(table.table)


if __name__ == '__main__':
    print_torrent_table()

