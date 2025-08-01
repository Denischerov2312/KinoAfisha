import requests
import os
import json
from bs4 import BeautifulSoup as Soup
from time import sleep
from os.path import join, split
from urllib.parse import unquote



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


def parse_and_save():
    films_data = []
    try:
        url = r'https://nn.kinoafisha.info/movies/'
        response = requests.get(url)
        response.raise_for_status()
        check_for_redirect(response)
        films_soup = Soup(response.text, 'html.parser')
        soups = films_soup.select_one('.movieList-grid').select('.grid_cell4')
        for soup in soups:
            film = {
                'title': get_title(soup),
                'genre': get_genre(soup),
                'year': get_year(soup),
                'country': get_country(soup),
                'img_url': get_img_url(soup),
                'ticket_url': get_ticket_url(soup)
            }
            films_data.append(film)
            download_image(film['img_url'], 'film_covers')
        with open(r'films.json', 'w', encoding='utf8') as file:
            json.dump(films_data, file, ensure_ascii=False)
    except ConnectionError:
        print('Подключение отсутствует')
        sleep(10)


if __name__ == '__main__':
    parse_and_save()