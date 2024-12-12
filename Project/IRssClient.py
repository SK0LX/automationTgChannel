from urllib.parse import urlparse, urlunparse

from bs4 import BeautifulSoup
from typing import List
import feedparser
import Post_object
from IDataBase import IDataBase


class IRssClient:
    def get_posts(self, url: str, count: int) -> List[Post_object]:
        raise NotImplementedError


class RssClient(IRssClient):
    def __init__(self, db: IDataBase):
        self.db = db
        self.visitedPosts = db.load_visited_posts()

    def get_posts(self, url: str, count: int) -> List[Post_object]:
        posts = []
        self.update_visited_posts()
        try:
            # Получаем RSS-канал
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/117.0.0.0 Safari/537.36'}
            feed = feedparser.parse(url, request_headers=headers)

            if feed.bozo:
                raise ValueError(f"Ошибка чтения RSS: {feed.bozo_exception}")

            for entry in feed.entries:
                if len(posts) == count:
                    break
                # Проверяем, есть ли дата публикации
                if 'published_parsed' in entry:
                    post_time = entry.published_parsed
                else:
                    print(f"Пропущен пост без даты публикации: {entry.title}")
                    continue

                # Если пост старый, пропускаем его
                if entry.link in self.visitedPosts:
                    continue
                link = self._shorten_url(entry.link)

                # Извлекаем чистый текст из summary
                summary_html = entry.summary
                summary_text = BeautifulSoup(summary_html, 'html.parser').get_text()

                # Формируем текст поста
                post_text = f"{entry.title}\n\n{summary_text}\n\n"
                if link not in self.visitedPosts:
                    posts.append(Post_object.Post(post_text, link))
                    self.db.add_visited_post(link)
        except Exception as e:
            print(f"Произошла ошибка при парсинге RSS: {e}")
        return posts  # Возвращаем массив с постами

    def _shorten_url(self, url):
        """Удаляет параметры запроса из URL."""
        parsed_url = urlparse(url)
        shortened_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        return shortened_url
    
    def update_visited_posts(self):
        self.visitedPosts = self.db.load_visited_posts()
