from bs4 import BeautifulSoup
from collections import OrderedDict
from ebooklib import epub
from pathlib import Path
from string import ascii_lowercase as letters
import requests


def get_list_url(letter):
    return f"https://www.lieder-archiv.de/lieder_sammlung_{letter}.html"


def _get_song_list(list_soup):
    ul = list_soup.find('ul', class_='list')
    links = [a['href'] for a in ul.find_all('a', href=True)]
    return links


def get_song_list(list_url):
    soup = BeautifulSoup(requests.get(list_url).text, 'html.parser')
    return _get_song_list(soup)


def _get_song_title(song_soup):
    return song_soup.find('div', class_='heading').find('h2').text


def get_song_title(song_url):
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    return _get_song_title(soup)


def _get_song_text(song_soup):
    return song_soup.find('div', class_='lyrics-container')


def get_song_text(song_url):
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    return _get_song_text(soup)


def _get_score_image_url(song_soup):
    return song_soup.find('img', class_='score', src=True)['src']


def get_score_image_url(song_url):
    soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
    return _get_score_image_url(soup)


def save_score_image(song_url):
    """
    Saves the score PNG under ./score_images/
    :param image_url: URL of the song page
    :return: path to created file
    """
    image_url = get_score_image_url(song_url)
    folder = Path('./score_images')
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / image_url.split('/')[-1]

    if not out_path.is_file():
        response = requests.get(image_url)

        with open(out_path, 'wb') as file:
            file.write(response.content)

    return out_path


class Song:
    def __init__(self, song_url):
        song_soup = BeautifulSoup(requests.get(song_url).text, 'html.parser')
        self.title = _get_song_title(song_soup)
        self.score_img = save_score_image(song_url)
        self.text = _get_song_text(song_soup)

    def __str__(self):
        return f"==== SONG ====" \
               f"Title: {self.title}" \
               f"Sheet Music: {self.score_img}" \
               f"Text: {self.text}"


if __name__ == '__main__':
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('liederarchiv-liederbuch')
    book.set_title('Lieder Archiv - Liederbuch')
    book.set_language('de')

    contents = OrderedDict()

    for char in "a":         # letters:
        songs = get_song_list(get_list_url(char))
        per_letter_contents = []

        for _song_url in songs:
            song = Song(_song_url)
            per_letter_contents.append(song)

        contents[char.upper()] = per_letter_contents

    print(contents)
