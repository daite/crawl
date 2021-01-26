#!/usr/bin/env python3
# only korean tv show (kt/search)

import gevent
from gevent import monkey; monkey.patch_all()
from bs4 import BeautifulSoup
from terminaltables import AsciiTable
import requests

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}

def get_magnet(bbs_url):
    doc = requests.get(bbs_url, headers=headers).text
    magnet_data = eval(doc.split('tt = ')[-1].split(';')[0])['hs']
    return "magnet:?xt=urn:btih:" + magnet_data

def main():
    table_data = []
    keyword = input('input the keyword: ')
    web_url = attack_server()
    url = '{}/kt/search?p&q={}'.format(web_url, keyword)
    r = requests.get(url, headers=headers)
    data = r.text.split('pageItems = ')
    dict_data = eval(data[-1].split(';')[0])
    titles = []
    bbs_urls = []
    for i in dict_data:
        title = i['fn']
        bbs_id = i['id']
        bbs_url = '{}/kt/read?p={}&se=1'.format(web_url, bbs_id)
        titles.append(title)
        bbs_urls.append(bbs_url)
    
    jobs = [gevent.spawn(get_magnet, url) for url in bbs_urls]
    gevent.joinall(jobs)
    m = [job.value for job in jobs]
    for title, magnet in zip(titles, m):
        table_data.append([title, magnet])
    table_data.insert(0, ['Title', 'Magnet'])
    table = AsciiTable(table_data)
    print(table.table)

def find_the_first_available_server():
    twitter_url = 'https://twitter.com/torrentube'
    r = requests.get(twitter_url)
    soup = BeautifulSoup(r.text, 'lxml')
    urls = [x['title'] for x in soup.find_all("a", title=True) 
            if x['title'].startswith('https')]
    return urls[1]

def attack_server():
    base_url = 'https://{}.torrentube.net/'
    for num in range(1, 100):
        try:
            url = base_url.format(num)
            print('\r[*] Attacking server {}'.format(url),
                  end='', flush=True)
            _ = requests.get(url, headers=headers)
            print()
            return url
        except:
            continue

if __name__ == '__main__':
    main()
