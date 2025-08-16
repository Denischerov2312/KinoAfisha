import jinja2
import json
import os
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
from livereload import Server
from more_itertools import chunked
from math import ceil
from urllib.parse import urljoin


COUNT_IN_PAGE = 10
DEST_FOLDER = 'pages/'


environment = jinja2.Environment()
template = environment.from_string("Hello, {{ name }}!")
template.render(name="World")


def get_file_info(filepath):
    with open(filepath, 'r', encoding='utf8') as file:
        file_info = json.load(file)
    return file_info


def on_reload():
    env = jinja2.Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')
    os.makedirs(DEST_FOLDER, exist_ok=True)

    films = get_file_info('films.json')
    pages = chunked(films, COUNT_IN_PAGE)
    page_count = ceil(len(films) / COUNT_IN_PAGE)
    for number, page in enumerate(pages, 1):
        filepath = urljoin(DEST_FOLDER, f'index{number}.html')
        if number == 1:
            filepath = urljoin(DEST_FOLDER, 'index.html')
        rendered_page = template.render(
            films=page,
            page_count=page_count,
            current_page=number,
            dest_folder=DEST_FOLDER
        )
        with open(filepath, 'w', encoding='utf8') as file:
            file.write(rendered_page)


def watch_file():
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.watch('style.css', on_reload)
    server.serve(root='.', default_filename='pages/index.html')


if __name__ == '__main__':
    watch_file()