import unittest
from datetime import datetime

from tg.Bot.Scripts.post import Post
from tg.Bot.Scripts.post_status import PostStatus


class TestPost(unittest.TestCase):
    def setUp(self):
        self.post_id = 1
        self.post_content = "Test content"
        self.post_creation_time = datetime.now()
        self.post = Post(self.post_id, self.post_content, self.post_creation_time)

    def test_initial_status(self):
        self.assertEqual(self.post.status, PostStatus.NOT_CHECKED)

    def test_accept_post(self):
        self.post.accept_post()
        self.assertEqual(self.post.status, PostStatus.ACCEPTED)

    def test_decline_post(self):
        self.post.decline_post()
        self.assertEqual(self.post.status, PostStatus.DECLINED)

    def test_post_attributes(self):
        self.assertEqual(self.post.id, self.post_id)
        self.assertEqual(self.post.content, self.post_content)
        self.assertEqual(self.post.creation_time, self.post_creation_time)


if __name__ == "__main__":
    unittest.main()
