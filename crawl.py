import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from pathlib import Path
from random import sample

def start_with_hash(link):
    if re.match(r"^#",link):
        return True
    else:
        return False

def start_with_http(link):
    try:
        if re.match(r"^http",link):
            return True
        else:
            return False
    except TypeError:
        print("TypeError no http?")
        return False

def same_hostname(link_1,link_2):
    l_1 = urlparse(link_1)
    l_2 = urlparse(link_2)

    return (l_1.hostname == l_2.hostname)

def is_rss(link):
    if re.search(r"rss",link) or re.search(r"feed",link) or re.search(r"xml",link) or re.search(r"\.atom",link):
        if re.search(r"feedback",link):
            return False
        else:
            return True
    else:
        return False

def check_link_in_file(link,file_path):
    p = Path(file_path)
    links = p.read_text().split("\n")
    if link in links:
        return False
    else:
        links.append(link)
        p.write_text("\n".join(links))
        return True

def link_is_new(link):
    return check_link_in_file(link,"links.txt")

def keep_rss(links):
    rss = [l for l in links if is_rss(l)]
    for link in rss:
        if check_link_in_file(link,"rss.txt"):
            print("FOUND!!! ",link)

def not_blacklisted(link):
    black_list = ["facebook","google","instagram",
                  "pinterest","linkedin","flickr"]
    l = urlparse(link)
    for b in black_list:
        if re.search(b,l.hostname):
            return False

    return True

def sample_crawled_links(n):
    p = Path("links.txt")
    links = p.read_text().split("\n")
    return sample(links,n)

def get_links(link):

    if link_is_new(link) and not_blacklisted(link):
        print(link)
        try:
            respond = requests.get(link)
            soup = BeautifulSoup(respond.text, 'lxml')
            return set([l.get("href") for l in soup.find_all("a")
                                        if (start_with_http(l.get("href")) and (not start_with_hash(l.get("href"))))])
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError")

def recursive_crawl(start_link):
    # print(start_link)
    links = get_links(start_link)
    if links:
        keep_rss(links)
        try:
            for l in list(links)+sample_crawled_links(100):
                recursive_crawl(l)
        except ValueError:
            print("ValueError list+sample_crawled_links")
            for l in links:
                recursive_crawl(l)


start_link = "http://www.malaysia-today.net/"
recursive_crawl(start_link)
