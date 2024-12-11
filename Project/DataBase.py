from typing import Dict, List

import psycopg2

from IDataBase import IDataBase


class DatabaseHandler(IDataBase):
    def __init__(self, config):
        self.db_config = config
        self.connection = None
        self.cursor = None

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.cursor = self.connection.cursor()
        except Exception as e:
            raise ConnectionError(f"Ошибка подключения к базе данных: {e}")

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def add_post(self, content: str, source: str, topic_id: int) -> None:
        self.connect()
        query = "INSERT INTO posts (content, source, is_accepted, topic_id) VALUES (%s, %s, %s, %s)"
        try:
            self.cursor.execute(query, (content, source, False, topic_id))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка добавления поста: {e}")
        finally:
            print("отправил постик в бд")
            self.close()

    def add_visited_post(self, url: str) -> None:
        self.connect()
        query = "INSERT INTO visitedposts (url) VALUES (%s)"
        try:
            self.cursor.execute(query, (url,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка добавления посещенного поста: {e}")
        finally:
            self.close()
            
    def load_visited_posts(self) -> List[str]:
        self.connect()
        query = "SELECT url FROM visitedposts"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        urls = [row[0] for row in rows]
        self.close()
        return urls

    def load_topics(self) -> Dict[str, int]:
        """:return Dict[topic_name: topic_id]"""
        self.connect()
        query = "SELECT name, id FROM topics"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close()
        return {row[0]: row[1] for row in rows}

    def load_prompts(self) -> Dict[int, str]:
        """:return Dict[site_id: prompt_text]"""
        self.connect()
        query = "SELECT site_id, prompt_text FROM prompts"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close()
        return {row[0]: row[1] for row in rows}

    def load_sites(self) -> Dict[int, str]:
        """:return Dict[site_id: site_url]"""
        self.connect()
        query = "SELECT id, site_url FROM sites"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close()
        return {row[0]: row[1] for row in rows}

    def site_id_to_topic_id(self) -> Dict[int, int]:
        """return Dict[site_id: topic_id]"""
        self.connect()
        query = "SELECT id, topic_id FROM sites"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.close()
        return {row[0]: row[1] for row in rows}
