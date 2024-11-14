import json
import time
from typing import List
import schedule
import requests

import Parser
from Filters import Filters


class Script:
    def __init__(self):
        self.key = "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"
        self.model = {"perplexity": "perplexity/llama-3.1-sonar-huge-128k-online",
                      "": "openai/o1-mini-2024-09-12",
                      "free": "meta-llama/llama-3.2-3b-instruct:free"
                      }
        self.parserHabr = Parser.Parser()
        self.filters = Filters()

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
                "Authorization": f"Bearer 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",
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
        message = ("Напиши sammary для этого поста. И сделай так, чтобы это можно было выложить в тг канал. "
                   "Красиво оформи смайликами и тд тп"
                   "А В конце просто, что информация была взята отсюда: "
                   f"Текст: {post}\n"  # Добавлено \n
                   "и здесь хэштеги - ключевые слова")
        return self.get_chat_response(message, self.model[model])

    def simple_summary(self) -> List[str]:
        posts = self.parserHabr.get_habr_posts()
        summary = list()
        if len(posts) >= 3:
            for i in range(3):
                print(i)
                summary.append(self.generate_summary(posts[i], "free"))
        return summary

    def simple_summary_with_filter(self, key_worlds=None) -> List[str]:
        summaries = self.simple_summary()
        if key_worlds is not None:
            key_worlds = key_worlds.split(",")
            filter_summaries = self.filters.filter_posts_by_hashtags(summaries, key_worlds)
            return filter_summaries
        return summaries

    def run_periodically(self):
        """Запускает обработку данных с заданной периодичностью."""
        summaries = self.simple_summary_with_filter("ИИ, Программирование")
        for summary in summaries:
            print(summary)


if __name__ == "__main__":
    script = Script()

    schedule.every(1).minutes.do(script.run_periodically)

    while True:
        schedule.run_pending()
        time.sleep(1)
