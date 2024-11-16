import psycopg2
from datetime import datetime


class DatabaseHandler:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def add_post(self, content, source):
        """
        Добавление поста в базу данных с уникальным topic_id
        :param content: текст поста
        :param source: источник поста
        """
        try:
            # Генерация нового topic_id
            topic_id = self.generate_new_topic_id()
            print(f"Новый Topic ID: {topic_id}")

            # Добавление новой темы
            self.cursor.execute("""
                INSERT INTO topics (id, name)
                VALUES (%s, %s);
            """, (topic_id, f"пост{topic_id}"))

            # Добавление поста
            self.cursor.execute("""
                INSERT INTO posts (content, created_at, source, is_accepted, topic_id)
                VALUES (%s, %s, %s, %s, %s);
            """, (content, datetime.now(), source, False, topic_id))

            # Сохранение изменений
            self.connection.commit()
            print("Пост успешно добавлен!")

        except Exception as e:
            print(f"Ошибка при добавлении поста: {e}")
            self.connection.rollback()

    def generate_new_topic_id(self):
        """
        Генерация нового уникального topic_id, который больше текущего максимального на 1
        :return: новый topic_id
        """
        try:
            self.cursor.execute("SELECT MAX(id) FROM topics;")
            max_topic_id = self.cursor.fetchone()[0]
            return (max_topic_id or 0) + 1  # Если таблица пуста, начинаем с 1
        except Exception as e:
            print(f"Ошибка при генерации нового topic_id: {e}")
            return 1  # В случае ошибки возвращаем 1
