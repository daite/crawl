#!/usr/bin/env python3

from terminaltables import AsciiTable
from bs4 import BeautifulSoup as BS
import requests
import re

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}


def trim_char(text):
    new = []
    for t in text:
        if not t  in ['\t', '\n', ' ']:
            new.append(t)
    return ''.join(new)


def main():
    table_data = []
    keyword = input('input the keyword: ')
    url = 'https://torrentwal.net/bbs/s.php?k={}'.format(keyword)
    r = requests.get(url, headers=headers, verify=False)
    soup = BS(r.text, 'lxml')
    trs = soup.find_all('tr', {'class': 'bg1'})
    for tr in trs:
        data = re.search('[0-9A-Z]+', tr.find('a')['href'].strip(
            'javascript:Mag_dn'))
        magnet = 'magnet:?xt=urn:btih:' + data.group()
        subject = trim_char(tr.find('td', {'class': 'subject'}).text)
        table_data.append([subject, magnet]) 
    table_data.insert(0, ['Title', 'Magnet'])
    table = AsciiTable(table_data)
    print(table.table)


if __name__ == '__main__':
    main()
