import psycopg2
from post import Post
from post_status import PostStatus

DB_CONFIG = {
    'host': 'localhost',
    'database': 'TgAuto',
    'user': 'postgres',
    'password': 'admin',
    'port': '5432'
}


class DBOperator:
    def __init__(self):
        self.connection = psycopg2.connect(**DB_CONFIG)
        self.cursor = self.connection.cursor()

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
