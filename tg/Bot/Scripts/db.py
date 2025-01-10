import psycopg2
from tg.Bot.Scripts.post import Post
from tg.Bot.Scripts.post_status import PostStatus
import yaml

with open("../../../core/config.yaml", "r", encoding="utf-8-sig") as config_file:
    config_data = yaml.safe_load(config_file)

DB_CONFIG = {
    'user': config_data['db']['user'],
    'password': config_data['db']['password'],
    'host': config_data['db']['host'],
    'database': config_data['db']['database']
}


class DBOperator:
    def __init__(self, group_id):
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()
        self.topics = self.get_topics_by_group(group_id)

    def update_group_topics(self, group_id):
        self.topics = self.get_topics_by_group(group_id)

    def get_admin_ids(self):
        try:
            self.cursor.execute("SELECT telegram_id FROM admins;")
            telegram_ids = self.cursor.fetchall()
            return [telegram_id[0] for telegram_id in telegram_ids]

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_admin_name(self, user_id):
        try:
            self.cursor.execute(f"SELECT username FROM admins WHERE telegram_id = {user_id};")
            username = self.cursor.fetchall()
            return username[0][0]

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_group_id(self, user_id):
        try:
            self.cursor.execute(f"SELECT group_id FROM admins WHERE telegram_id = {user_id};")
            group_id = self.cursor.fetchall()
            return group_id[0][0]

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

    def get_topics_by_group(self, group_id):
        try:
            self.cursor.execute(f"SELECT name, id FROM topics WHERE group_id = {group_id};")
            topics = {}
            lines = self.cursor.fetchall()
            for line in lines:
                topics[str(line[0])] = int(line[1])
            return topics

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_posts_by_topic_and_group_id(self, topic_name, group_id):
        try:
            topic_id = self.topics[topic_name]
            self.cursor.execute(f"SELECT id, content, created_at, is_accepted FROM posts WHERE is_accepted = FALSE "
                                f"AND topic_id = {topic_id} AND group_id = {group_id};")
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
