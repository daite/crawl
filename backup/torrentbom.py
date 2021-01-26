#!/usr/bin/env python3

import gevent
from gevent import monkey; monkey.patch_all()
from bs4 import BeautifulSoup
from terminaltables import AsciiTable
import requests
import re

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}

web_url = "https://torrent.vet/"

def get_magnet(bbs_url):
    doc = requests.get(bbs_url, headers=headers).content
    soup = BeautifulSoup(doc, 'lxml')
    r = [x.text for x in soup.find_all('li') if 'magnet' in x.text]
    if len(r) == 0:
        return "NO MAGNET DATA"
    else:
        magnet_data = re.search("magnet.*", r[0])[0]
        return magnet_data

def main():
    table_data = []
    keyword = input('input the keyword: ')
    url = '{}search.php?keyword={}'.format(web_url, keyword)
    doc = requests.get(url, headers=headers).content
    soup = BeautifulSoup(doc, 'lxml')
    s = soup.find_all("a", {"class": "sch_res_title"})
    titles = []
    bbs_urls = []
    for i in s:
        titles.append(i.text)
        bbs_urls.append(web_url + i['href'])
    jobs = [gevent.spawn(get_magnet, url) for url in bbs_urls]
    gevent.joinall(jobs)
    m = [job.value for job in jobs]
    for title, magnet in zip(titles, m):
        table_data.append([title, magnet])
    table_data.insert(0, ['Title', 'Magnet'])
    table = AsciiTable(table_data)
    print(table.table)


if __name__ == '__main__':
    main()
