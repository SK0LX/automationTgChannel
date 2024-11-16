import re

from bs4 import BeautifulSoup
import requests

import Post_object


class Parser:
    def __init__(self):
        self.habr_link = "https://habr.com/ru/posts/"

    def get_habr_posts(self):
        posts = []
        try:
            html = requests.get(self.habr_link)
            html.raise_for_status()  # Проверка кода ответа (200 - OK)
            soup = BeautifulSoup(html.content, 'html.parser')
            post_elements = soup.find_all('div', class_='tm-post-snippet__content')

            for post_element in post_elements:
                post_text = ""
                paragraphs = post_element.find_all('p')
                for paragraph in paragraphs:
                    post_text += (paragraph.text.strip() + "\n")
                post_text += "\nСсылка, откуда был взят пост : https://habr.com/ru/posts/"

                posts.append(Post_object.Post(post_text, self.habr_link))  # Добавляем текст поста в массив

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе к Habr: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")

        return posts  # Возвращаем массив с постами
