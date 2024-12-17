from Bot.post_status import PostStatus


class Post:
    def __init__(self, id, content, creation_time):
        self.id = id
        self.content = content
        self.creation_time = creation_time
        self.status = PostStatus.NOT_CHECKED

    def accept_post(self):
        self.status = PostStatus.ACCEPTED

    def decline_post(self):
        self.status = PostStatus.DECLINED
