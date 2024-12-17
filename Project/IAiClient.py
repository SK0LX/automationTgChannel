import json

import requests


class IAiClient:
    def send_message(self, model: str, message: str) -> str:
        raise NotImplementedError


class OpenRouterClient(IAiClient):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send_message(self, model: str, message: str) -> str:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            data=json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": message}]
            }),
        )
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Ошибка API: {response.status_code}, {response.text}")
