import requests
import os
import json
from bs4 import BeautifulSoup as Soup
from time import sleep
from os.path import join, split
from urllib.parse import unquote
from dotenv import load_dotenv
from datetime import date

load_dotenv()
PARSING_URL = os.getenv('PARSING_URL', default=r'https://nn.kinoafisha.info/movies/')
FILMS_FILE = os.getenv('FILMS_FILE', default=r'films.json')
DATE = os.getenv('DATE', default=date.today())


def get_title(soup):
    return soup.select_one('.movieItem_title').text.strip()


def get_genre(soup):
    return soup.select_one('.movieItem_genres').text.split(', ')


def get_year(soup):
    return int(soup.select_one('.movieItem_year').text.split(', ')[0].strip())


def get_country(soup):
    return soup.select_one('.movieItem_year').text.split(', ')[1].strip()


def get_img_url(soup):
    return soup.select_one('.picture_image')['src'].strip()


def get_ticket_url(soup):
    return soup.select_one('.movieItem_button-tickets')['href']


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_image(url, folder):
    try:
        response = requests.get(url)
        filename = unquote(split(url)[-1])
        response.raise_for_status()
        check_for_redirect(response)
        os.makedirs(folder, exist_ok=True)
        filepath = join(folder, filename).replace('\\', '/')
        with open(filepath, 'wb') as file:
            file.write(response.content)
        return filepath
    except requests.exceptions.HTTPError:
        return None


def save(films_data):
    with open(FILMS_FILE, 'w', encoding='utf8') as file:
        json.dump(films_data, file, ensure_ascii=False)


def get_response(url):
    while True:
        try:
            response = requests.get(url, params={'date': DATE})
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except ConnectionError:
            print('Подключение отсутствует')
            sleep(10)


def parse():
    films_data = []
    response = get_response(PARSING_URL)
    films_soup = Soup(response.text, 'html.parser')
    soups = films_soup.select_one('.movieList-grid').select('.grid_cell4')
    for soup in soups:
        film = {
            'title': get_title(soup),
            'genre': get_genre(soup),
            'year': get_year(soup),
            'country': get_country(soup),
            'img_path': download_image(get_img_url(soup), 'film_covers'),
            'ticket_url': get_ticket_url(soup)
        }
        films_data.append(film)
    return films_data


def main():
    films_data = parse()
    save(films_data)


if __name__ == '__main__':
    main()
