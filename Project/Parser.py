import json

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
        return posts# Возвращаем массив с постами

    def _shorten_url(self, url):
        """Удаляет параметры запроса из URL."""
        parsed_url = urlparse(url)
        shortened_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
        return shortened_url
