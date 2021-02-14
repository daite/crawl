#!/usr/bin/env python3

from terminaltables import AsciiTable
from http.client import HTTPConnection
from bs4 import BeautifulSoup 
from functools import wraps
import requests
import time
import re
import os


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)',
}


def get_soup(url):
    r = requests.get(url, headers=headers)
    return BeautifulSoup(r.content, 'lxml')


def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        HTTPConnection.debuglevel = 1
        return func(*args, **kwargs)
    return wrapper


class SukebeScrapper:

    def __init__(self, search_words):
        self.search_words = search_words

    def get_all_torrent_data(self):
        all_data = []
        url = f'https://sukebei.nyaa.si/?f=0&c=0_0&q={self.search_words}'
        soup = get_soup(url)
        soup_data = soup.find_all('tr')
        for d in soup_data[1:]:
            td = d.find_all('td')
            title = td[1].find('a')['title'][:30]
            file_size = td[3].text
            magnet = td[2].find_all('a')[1]['href'].split('&')[0]
            date = td[4].text
            seeder = td[5].text
            leecher = td[6].text
            all_data.append([date, title, file_size, seeder, leecher, magnet])
        return all_data

    def get_all_image_links(self):
        links = []
        url = f'https://www.jav321.com/video/{self.search_words}'
        soup = get_soup(url)
        img_urls = soup.find_all('img', {'class': 'img-responsive'})
        for img in img_urls:
            img_url = img['src']
            if re.search(self.search_words, img_url):
                links.append(img_url)
        return links

    def download_all_images(self, image_links):
        if len(image_links) == 0:
            print(f"[-] Couldn't find any images from {self.search_words}")
            return
        cur_dir = os.path.abspath('.')
        down_dir = os.path.join(
        os.path.join(cur_dir, 'images'), self.search_words)
        print(f'[+] Downloading images from {self.search_words}')
        for image_url in image_links:
            cmd = f'wget -nc -q {image_url} -P {down_dir} &'
            os.system(cmd)
        time.sleep(1)
        os.system(f'open {down_dir}')

    @staticmethod
    def show(data, limit=10):
        if len(data) == 0:
            print("[-] There is no data!!")
            return
        table_data = [
            ['DATE', 'TITLE', 'FILE_SIZE', 'SEEDER', 'LEECHER', 'MAGNET'],
        ]
        for z in sorted(data[:limit], key=lambda k: int(k[3]), reverse=True):
            table_data.append(z)
            table = AsciiTable(table_data)
        print(table.table)


def main():
    search_words = input('input the search words: ')
    s = SukebeScrapper(search_words)
    links = s.get_all_image_links()
    s.download_all_images(links)
    data = s.get_all_torrent_data()
    s.show(data)


if __name__ == '__main__':
    main()