import psycopg2
from Bot.post import Post
from Bot.post_status import PostStatus

DB_CONFIG = {}


class DBOperator:
    def __init__(self):
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()
        self.topics = self.get_topics()

    def get_admin_ids(self):
        try:
            self.cursor.execute("SELECT telegram_id FROM admins;")
            telegram_ids = self.cursor.fetchall()
            return [telegram_id[0] for telegram_id in telegram_ids]

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_posts(self):
        try:
            self.cursor.execute("SELECT id, content, created_at, is_accepted FROM posts WHERE is_accepted = FALSE;")
            posts = []
            lines = self.cursor.fetchall()
            for line in lines:
                posts.append(Post(id=int(line[0]), content=line[1], creation_time=line[2]))
            return posts

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_topics(self):
        try:
            self.cursor.execute("SELECT name, id FROM topics;")
            topics = {}
            lines = self.cursor.fetchall()
            for line in lines:
                topics[str(line[0])] = int(line[1])
            return topics

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_posts_by_topic(self, topic_name):
        try:
            topic_id = self.topics[topic_name]
            self.cursor.execute(f"SELECT id, content, created_at, is_accepted FROM posts WHERE is_accepted = FALSE "
                                f"AND topic_id = {topic_id};")
            posts = []
            lines = self.cursor.fetchall()
            for line in lines:
                posts.append(Post(id=int(line[0]), content=line[1], creation_time=line[2]))
            return posts

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def update_post(self, post: Post):
        try:
            if post.status == PostStatus.DECLINED:
                self.cursor.execute(f"DELETE FROM posts WHERE id = {post.id};")
            elif post.status == PostStatus.ACCEPTED:
                self.cursor.execute(f"UPDATE posts SET is_accepted = TRUE WHERE id = {post.id};")

            if self.cursor.rowcount == 0:
                print(f"Не удалось найти пост с id {post.id} для обновления.")

            self.connection.commit()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
