import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import unquote
import os

url = "https://www.omnycontent.com/d/playlist/67122501-9b17-4d77-84bd-a93d00dc791e/3c31cad9-230a-4a5f-b487-a9de001adcdd/39cee2d4-8502-4b84-b11b-a9de001ca4cc/podcast.rss"
soup = BS(requests.get(url).content, 'lxml')
links = soup.find_all("media:content", type="audio/mpeg")
for link in links[10:20]:
    r = requests.head(link['url'])
    headers = r.headers
    down_url = headers['location']
    try:
        title = unquote(down_url.split(',')[1])
        title = title.lstrip("omny_clip_title:") + ".mp3"
        down_url = down_url.split('?')[0]
        cmd = 'wget "{}" -O "{}" &'.format(down_url, title)
        os.system(cmd)
    except:
        continue