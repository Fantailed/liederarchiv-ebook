from bs4 import BeautifulSoup
from ebooklib import epub
from pathlib import Path
import requests

BOOK = epub.EpubBook()


def get_list_url(letter):
    return f"https://www.lieder-archiv.de/lieder_sammlung_{letter}.html"


def get_song_list(list_url):
    soup = BeautifulSoup(requests.get(list_url).text, 'html.parser')
    ul = soup.find('ul', class_='list')
    links = [a['href'] for a in ul.find_all('a', href=True)]
    return links


def get_song_title(song_url):
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    return soup.find('div', class_='heading').find('h2').text


def _get_score_image_url(song_url):
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    return soup.find('img', class_='score', src=True)['src']


def save_score_image(song_url):
    """
    Saves the score PNG under ./score_images/
    :param song_url: URL of the song page
    :return: path to created file
    """
    song_url = _get_score_image_url(song_url)
    folder = Path('./score_images')
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / song_url.split('/')[-1]
    response = requests.get(song_url)

    with open(out_path, 'wb') as file:
        file.write(response.content)

    return out_path


if __name__ == '__main__':
    a_songs = get_song_list(get_list_url('a'))
    katze = a_songs[3]
    save_score_image(katze)
