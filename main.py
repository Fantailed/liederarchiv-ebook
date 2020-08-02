from bs4 import BeautifulSoup
from ebooklib import epub
from pathlib import Path
from PIL import Image
from string import ascii_lowercase as letters
import io
import requests


def get_list_url(letter):
    return f"https://www.lieder-archiv.de/lieder_sammlung_{letter}.html"


def _get_song_list(list_soup):
    ul = list_soup.find('ul', class_='list')
    links = list(dict.fromkeys([a['href'] for a in ul.find_all('a', href=True)]))
    return links


def get_song_list(list_url):
    soup = BeautifulSoup(requests.get(list_url).text, 'html.parser')
    return _get_song_list(soup)


def _get_song_title(song_soup):
    return song_soup.find('div', class_='heading').find('h2')


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
        self.title = _get_song_title(song_soup).text
        self.title_html = str(_get_song_title(song_soup))
        self.score_img = save_score_image(song_url)
        self.text = _get_song_text(song_soup)
        self.url = song_url
        self.filename = song_url.split('/')[-1]
        self.id = song_url.split('/')[-1].split('_')[-1].split('.')[0]
        # Create song HTML
        song_soup = BeautifulSoup(self.title_html, 'html.parser')
        new_img = song_soup.new_tag('img', src=self.score_img)
        song_soup.append(new_img)
        song_soup.append(self.text)
        self.html = str(song_soup)

    def __str__(self):
        return f"==== SONG ====\n" \
               f"Title: {self.title}\n" \
               f"Sheet Music: {self.score_img}\n" \
               f"Text: {self.text}\n"


if __name__ == '__main__':
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier('liederarchiv-liederbuch')
    book.set_title('Lieder Archiv - Liederbuch')
    book.set_language('de')
    book.add_metadata('DC', 'description', 'Alle Lieder von www.lieder-archiv.de in einem Buch!')
    book.add_metadata(None, 'copyright', 'Copyright © 1996-2020 Alojado Publishing')

    contents = {}

    for char in "a":         # letters:
        print(f"Processing songs starting with {char.upper()}...")

        songs = get_song_list(get_list_url(char))
        per_letter_contents = []

        for _song_url in songs:
            song = Song(_song_url)
            print(f"Current song: {song.title}")

            # Prepare image file
            image = Image.open(song.score_img)
            b = io.BytesIO()
            image.save(b, 'png')
            b_image = b.getvalue()
            book.add_item(epub.EpubItem(uid=song.id, file_name=str(song.score_img), media_type='image/png', content=b_image))

            chapter = epub.EpubHtml(title=song.title, file_name=song.filename, lang='de')
            chapter.content = song.html

            per_letter_contents.append(chapter)

        contents[char.upper()] = per_letter_contents

    spine_list = []
    section_tuple = []

    for k, v in contents.items():
        for item in v:
            book.add_item(item)
            spine_list.append(item)
        section_tuple.append((epub.Section(k), v))

    book.toc = section_tuple
    book.spine = spine_list
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub('Liederbuch.epub', book)
