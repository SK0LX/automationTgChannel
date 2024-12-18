from typing import List

from IAiClient import IAiClient
import Post_object


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
            message = (self.prompts[site_id])
            message += "Teкст {}".format(post.content)
            summary = self.ai_client.send_message(model, message)
            if self.summary_is_vallidate(summary):
                post.summary = f"{summary}\nИсточник: {post.link}"
                summaries.append(post)
        return summaries

    def simple_summary(self, posts: List[Post_object], model, count, site_id: int) -> List[Post_object]:
        """Создает краткие версии для списка постов."""
        if len(posts) >= count:
            return self.generate(posts[::count], model=model, site_id=site_id)
        return self.generate(posts, model=model, site_id=site_id)

    def summary_is_vallidate(self, summary):
        if summary is None:
            return False
        if len(summary) == 0:
            return False
        if len(summary) > 4096:
            return False
        return True
