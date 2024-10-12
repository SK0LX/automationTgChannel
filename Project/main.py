import json

import requests


class Script:
    def __init__(self):
        self.key = "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"
        self.model = {"perplexity": "perplexity/llama-3.1-sonar-huge-128k-online",
                      "gpt": "openai/o1-mini-2024-09-12"}

    def get_chat_response(self, message, model):
        """Отправляет сообщение в OpenRouter и возвращает ответ.
            Args:
              message (str): Сообщение для отправки.
              model: модель ИИ
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
            return reply
        else:
            print(f"Ошибка: {response.status_code}")
            print(response.text)
            return None