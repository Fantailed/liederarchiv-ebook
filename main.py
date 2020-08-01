from bs4 import BeautifulSoup
from ebooklib import epub
import requests

BOOK = epub.EpubBook()


def get_list_url(letter):
    return f"https://www.lieder-archiv.de/lieder_sammlung_{letter}.html"


def get_song_list(list_url):
    soup = BeautifulSoup(requests.get(list_url).text, 'html.parser')
    ul = soup.find('ul', class_='list')
    links = [a['href'] for a in ul.find_all('a', href=True)]
    return links


if __name__ == '__main__':
    print(get_song_list(get_list_url('a')))
