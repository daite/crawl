#!/usr/bin/env python3

from bs4 import BeautifulSoup
import requests
import sys
import os

headers = {'User-Agent': 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3)"\
            "AppleWebKit/537.36 (KHTML, like Gecko) "\
            "Chrome/66.0.3359.181 Safari/537.36"}

ffmpeg_command = 'ffmpeg -i "{}" -bsf:a aac_adtstoasc' \
    ' -vcodec copy -c copy -crf 50 "{}.mp4"'


def extract_information(url):
    #url = 'https://www3.nhk.or.jp/news/html/20200605/k10012458961000.html'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'lxml')
    title = soup.find('span', {'class': 'contentTitle'}).text
    param = soup.find('div', {'id': 'news_video'}).text
    return title, param

def main():
    url = sys.argv[1]
    title, param = extract_information(url)
    m3u8_url = 'https://nhks-vh.akamaihd.net/i/news/' \
               '{}/master.m3u8'.format(param)
    command = ffmpeg_command.format(m3u8_url, title)
    os.system(command)

if __name__ == '__main__':
    main()
