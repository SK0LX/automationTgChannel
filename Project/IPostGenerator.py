import time
from typing import List

import Post_object
from IAiClient import IAiClient


class IPostGenerator:
    def generate(self, posts: List[Post_object], model: str, site_id: int) -> List[Post_object]:
        raise NotImplementedError

    def simple_summary(self, posts: List[Post_object], model, count, site_id: int) -> List[Post_object]:
        raise NotImplementedError


class PostGenerator(IPostGenerator):
    def __init__(self, ai_client: IAiClient, prompts: dict):
        self.ai_client = ai_client
        self.prompts = prompts

    def generate(self, posts: List[Post_object], model: str, site_id: int) -> List[Post_object]:
        summaries = []
        for post in posts:
            message = self.prompts[site_id].format(post.content)
            summary = self.ai_client.send_message(model, message)
            post.summary = f"{summary}\nИсточник: {post.link}"
            summaries.append(post)
        return summaries

    def simple_summary(self, posts: List[Post_object], model, count, site_id: int) -> List[Post_object]:
        """Создает краткие версии для списка постов."""
        if len(posts) >= count:
            return self.generate(posts[::count], model=model, site_id=site_id)
        return self.generate(posts, model=model, site_id=site_id)
