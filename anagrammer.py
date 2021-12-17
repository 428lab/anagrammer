# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as BS
import re
import sys
import urllib
from tqdm import tqdm


try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

def getName(url):
    names = []
    usock = urllib.request.urlopen(url)
    data = usock.read()
    usock.close()
    soup = BS(data,features="html.parser")
    table_list = soup.find('table', {'class':'table_list'})
    if table_list: 
        for name in table_list.text.split():
            names.append(name)
    return names


def getLinks(base_url, urls):
    print('**',base_url)
    reqs = requests.get(base_url)
    soup = BS(reqs.text, 'html.parser')

    if soup.title == None:
        return
    
    if '女性' not in soup.title.string and \
       '男性' not in soup.title.string and \
       '姓' not in soup.title.string and \
       '欧羅巴人名録' != soup.title.string:
        return 
    
    for link in soup.find_all('a'):
        if '#index' in link.get('href'):
            continue
        if './' == link.get('href'):
            continue
        if '..' == link.get('href'):
            continue
        if 'http' in link.get('href'):
            continue
        if 'javascript:void(0)' in link.get('href'):
            continue
        if './search' in link.get('href'):
            continue
        url = urllib.parse.urljoin(base_url , link.get('href'))
        if url not in urls:
            #getName(url, src)
            urls.append(url )
            getLinks(url, urls)


def search_anagram(url, src_name):
    urls = []
    getLinks(url, urls)

    sorted_src_name = ''.join(set(sorted(src_name)))
    #print('sorted_src_name',sorted_src_name)
    candidate_names = []
    for url in tqdm(urls):
        for name in getName(url):
            katakana = re.compile(r'[\u30A1-\u30F4・ー]+')
            for kana in katakana.findall(name):
                sorted_kana = ''.join(set(sorted(kana)))
                #print('sorted_kana',sorted_kana)
                included = True
                for c in sorted_kana:
                    if c not in sorted_src_name:
                        included = False
                if included:
                    candidate_names.append((url, name))
    return candidate_names


if __name__ == '__main__':
    src_name = sys.argv[1]
    print('src name',src_name)
    url = 'https://www.worldsys.org/europe/'

    candidate_names = search_anagram(url, src_name)
    if len(candidate_names):
        for url, candidate_name in candidate_names:
            print(url, candidate_name)
    else:
        print('not found')

