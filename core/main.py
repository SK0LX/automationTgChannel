import json
import time
from typing import List
import schedule
import requests

import DataBase
import Parser
import Post_object
from Filters import Filters


class Script:
    def __init__(self, count: int):
        self.key = "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"
        self.model = {
            "perplexity": "perplexity/llama-3.1-sonar-huge-128k-online",
            "": "openai/o1-mini-2024-09-12",
            "free": "meta-llama/llama-3.2-3b-instruct:free",
            "free2": "liquid/lfm-40b:free"
        }
        self.parserHabr = Parser.Parser_Habr()
        self.parserE1 = Parser.ParserE1()
        self.filters = Filters()
        # Настройки подключения
        db_config = {
            "host": "localhost",  # Замените на ваш хост
            "database": "db",  # Имя базы данных
            "user": "admin",  # Пользователь базы данных
            "password": "admin"  # Пароль пользователя
        }

        self.db = DataBase.DatabaseHandler(db_config)

        self.topic_id = self.db.loadTopics()
        self.prompts = self.db.loadPromts()
        self.count = count

    def get_chat_response(self, message, model):
        """Отправляет сообщение в OpenRouter и возвращает ответ.
         Args:
          message (str): Сообщение для отправки.
          model: модель ИИ (брать из словарика моделей)
         Returns:
          str: Ответ от OpenRouter.
         """
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.key}",
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            })
        )

        if response.status_code == 200:
            data = response.json()
            reply = data
            return self.get_chat_message(reply)
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return None

    def get_chat_message(self, message):
        try:
            return message["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            print(f"Ошибка при получении сообщения: {e}")
            time.sleep(10)  # Подождать перед повторной попыткой
            return self.get_chat_message(message)

    def generate_summary(self, post, model, name_topic):
        message = (
            self.prompts[self.topic_id[name_topic]]
            .format(post.content)
        )
        answer_gpt = self.get_chat_response(message, self.model[model])
        post.summary = answer_gpt + f"\nИнформация была взята отсюда: {post.link}"
        return post

    def simple_summary(self, posts: List[Post_object], count, name_topic) -> List[Post_object]:
        """Создает краткие версии для списка постов."""
        summary = []
        if len(posts) >= count:
            for i in range(count):
                time.sleep(10)
                print(f"Обрабатывается пост {i + 1}")
                summary.append(self.generate_summary(posts[i], "free", name_topic=name_topic))
        return summary

    def simple_summary_with_filter(self, posts: List[Post_object], count, name_topic, key_worlds=None) -> List[
        Post_object]:
        """Создает краткие версии постов и фильтрует их по ключевым словам."""
        summaries = self.simple_summary(posts, count, name_topic=name_topic)
        if key_worlds:
            key_worlds = key_worlds.split(",")
            filter_summaries = self.filters.filter_posts_by_hashtags(summaries, key_worlds)
            return filter_summaries
        return summaries

    def generated_posts(self, count, name_topic, parser, key_worlds=None):
        self.db.connect()
        posts = parser(count)  # Ожидается, что вернет список постов
        summaries = None
        if name_topic == "IT news":
            summaries = self.simple_summary_with_filter(posts, count, name_topic=name_topic, key_worlds=key_worlds)
        else:
            summaries = posts
            for summary in summaries:
                summary.summary = summary.content
        for summary in summaries:
            summary.topic_id = self.topic_id[name_topic]
            self.db.add_post(summary.summary, summary.link, summary.topic_id)
        self.db.close()

    def generated_summary_Habr(self, count, key_worlds=None):
        self.generated_posts(count=count, name_topic="IT news", parser=self.parserHabr.get_habr_posts, key_worlds=key_worlds)

    def generated_summary_E1(self, count, key_worlds=None):
        self.generated_posts(count=count, name_topic="Ekb news", parser=self.parserE1.get_E1_posts, key_worlds=key_worlds)

    def run_periodically(self):
        """Запускает обработку данных с заданной периодичностью."""
        self.generated_summary_Habr(self.count)
        self.generated_summary_E1(self.count)


if __name__ == "__main__":
    script = Script(1)

    script.run_periodically()

    schedule.every(1).hours.do(script.run_periodically)

    while True:
        schedule.run_pending()
        time.sleep(1)
