import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import feedparser
from urllib.parse import urlparse, urlunparse
import Post_object


class Parser_Habr:
    def __init__(self):
        self.rss_link = "https://habr.com/ru/rss/"
        self.last_processed_time = None  # Время последнего обработанного поста
        self.set_post = set()

    def get_habr_posts(self, count):
        posts = []
        try:
            # Получаем RSS-канал
            feed = feedparser.parse(self.rss_link)

            if feed.bozo:
                raise ValueError(f"Ошибка чтения RSS: {feed.bozo_exception}")

            for entry in feed.entries:
                if posts.count == count:
                    break
                # Проверяем, есть ли дата публикации
                if 'published_parsed' in entry:
                    post_time = entry.published_parsed
                else:
                    print(f"Пропущен пост без даты публикации: {entry.title}")
                    continue

                # Если пост старый, пропускаем его
                if entry.link in self.set_post:
                    continue
                link = self._shorten_url(entry.link)
                self.set_post.add(link)
                # Формируем текст поста
                post_text = f"{entry.title}\n\n{entry.summary}\n\nСсылка на пост: {link}"
                posts.append(Post_object.Post(post_text, link))

            # Обновляем время последнего обработанного поста
            if feed.entries:
                latest_post_time = max(entry.published_parsed for entry in feed.entries if 'published_parsed' in entry)
                self.last_processed_time = latest_post_time

        except Exception as e:
            print(f"Произошла ошибка при парсинге RSS: {e}")
        return posts  # Возвращаем массив с постами

    def _shorten_url(self, url):
        """Удаляет параметры запроса из URL."""
        parsed_url = urlparse(url)
        shortened_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        return shortened_url


class ParserE1:
    def __init__(self):
        self.base_url = "https://www.e1.ru/text/"
        self.set_post = set()

    def get_E1_posts(self, count) -> List[Post_object.Post]:
        """Парсит новости с главной страницы E1."""
        try:
            response = requests.get(self.base_url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()  # Проверяем на ошибки HTTP
        except requests.RequestException as e:
            print(f"Ошибка при получении данных с сайта: {e}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        posts = []

        # Ищем статьи
        articles = soup.find_all("article", {"data-test": "archive-record-item"})
        for article in articles:
            if posts.count == count:
                break
            # Ищем ссылку на новость
            link_tag = article.find("a", {"data-test": "archive-record-image"})
            if link_tag and "href" in link_tag.attrs:
                link = link_tag["href"]
                if not link.startswith("http"):
                    link = f"https://www.e1.ru{link}"
                title_div = article.find("div", class_="eQ4k7")
                title = title_div.text.strip() if title_div else "Без заголовка"
                if link not in self.set_post:
                    posts.append(Post_object.Post(title, link))
                    self.set_post.add(link)

        return posts
