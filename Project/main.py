import json
import time
from typing import List
import schedule
import requests

import BaseDate
import Parser
import Post_object
from Filters import Filters


class Script:
    def __init__(self, count:int):
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
            "database": "postgres",  # Имя базы данных
            "user": "postgres",  # Пользователь базы данных
            "password": "Lfybbk_2005"  # Пароль пользователя
        }

        self.db = BaseDate.DatabaseHandler(db_config)

        self.topic_id = self.db.loadTopics()
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

    def generate_summary(self, post, model):
        message = (
                "Напиши яркую и привлекательную сводку для Telegram-поста, не более 10-15 строк."
                "Текст должен быть информативным, интригующим и мотивировать читателя на прочтение всего поста."
                " Используй эмодзи для улучшения восприятия."
                " Сводка должна чётко передавать суть поста без лишних подробностей."+

                f"Текст поста:{post.content}"+
                "В конце добавь хэштеги. Их возьми из поста(если есть или сам придумай, основополагаясь на текст):" +
                "Хэштеги: (и здесь должно быть 3 хэштега))"+
                "В конце добавь хэштеги, используя предоставленные ключевые слова. Избегай ссылок, рекламы и слов-паразитов. Оформление должно быть стильным и привлекательным."
        )
        answer_gpt = self.get_chat_response(message, self.model[model])
        post.summary = answer_gpt + f"\nИнформация была взята отсюда: {post.link}"
        return post

    def simple_summary(self, posts: List[Post_object], count) -> List[Post_object]:
        """Создает краткие версии для списка постов."""
        summary = []
        if len(posts) >= count:
            for i in range(count):
                time.sleep(10)
                print(f"Обрабатывается пост {i + 1}")
                summary.append(self.generate_summary(posts[i], "free"))
        return summary

    def simple_summary_with_filter(self, posts: List[Post_object], count, key_worlds=None) -> List[Post_object]:
        """Создает краткие версии постов и фильтрует их по ключевым словам."""
        summaries = self.simple_summary(posts, count)
        if key_worlds:
            key_worlds = key_worlds.split(",")
            filter_summaries = self.filters.filter_posts_by_hashtags(summaries, key_worlds)
            return filter_summaries
        return summaries

    def generated_summary_Habr(self, count, key_worlds=None):
        """Генерация и сохранение сводок с Habr."""
        self.db.connect()
        posts = self.parserHabr.get_habr_posts(count)  # Ожидается, что вернет список постов
        if posts is None or not isinstance(posts, list):
            print("Ошибка: parserHabr.get_habr_posts() не вернул список постов.")
            return

        summaries = self.simple_summary_with_filter(posts, count, key_worlds)
        for summary in summaries:
            summary.topic_id = self.topic_id["IT"]
            self.db.add_post(summary.summary, summary.link, summary.topic_id)
        self.db.close()

    def generated_summary_E1(self, count, key_worlds=None):
        """Генерация и сохранение сводок с E1."""
        self.db.connect()
        posts = self.parserE1.get_E1_posts(count)  # Ожидается, что вернет список постов
        print(len(posts))
        if posts is None or not isinstance(posts, list):
            print("Ошибка: parserE1.get_E1_posts() не вернул список постов.")
            return

        for post in posts:
            time.sleep(10)
            post.summary = post.content + f"\n**Информация была взята отсюда: {post.link}**"
            post.topic_id = self.topic_id["NEWS"]
            self.db.add_post(post.summary, post.link, post.topic_id)
        self.db.close()

    def run_periodically(self): 
        """Запускает обработку данных с заданной периодичностью."""
        self.generated_summary_Habr(self.count)
        self.generated_summary_E1(self.count)


if __name__ == "__main__":  
    script = Script(5)

    schedule.every(1).seconds.do(script.run_periodically)

    while True:
        schedule.run_pending()
        time.sleep(1)
