import psycopg2


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

    def add_post(self, content, source, topic_id):
        """
        Добавление поста в базу данных с уникальным topic_id
        :param content: текст поста
        :param source: источник поста
        :param topic_id: номер топика
        """
        try:
            self.cursor.execute("""
                INSERT INTO posts (content, source, is_accepted, topic_id)
                VALUES (%s, %s, %s, %s);
            """, (content, source, False, topic_id))

            # Сохранение изменений
            self.connection.commit()
            print("Пост успешно добавлен!")

        except Exception as e:
            print(f"Ошибка при добавлении поста: {e}")
            self.connection.rollback()

    def loadTopics(self):
        """Загрузка топиков из базы данных"""
        try:
            # Убедиться, что соединение активно
            if not self.connection:
                self.connect()

            # Выполнить запрос
            self.cursor.execute("SELECT name, id FROM topics")
            rows = self.cursor.fetchall()

            # Преобразование в словарь
            name_description_dict = {row[0]: row[1] for row in rows}

            return name_description_dict
        except Exception as e:
            print(f"Ошибка при загрузке топиков: {e}")
            return {}

    def loadPromts(self):
        """Загрузка топиков из базы данных"""
        try:
            # Убедиться, что соединение активно
            if not self.connection:
                self.connect()

            # Выполнить запрос
            self.cursor.execute("SELECT site_id, prompt_text FROM prompts")
            rows = self.cursor.fetchall()

            # Преобразование в словарь
            name_description_dict = {row[0]: row[1] for row in rows}

            return name_description_dict
        except Exception as e:
            print(f"Ошибка при загрузке топиков: {e}")
            return {}

    def loadSites(self):
        """Загрузка топиков из базы данных"""
        try:
            # Убедиться, что соединение активно
            if not self.connection:
                self.connect()

            # Выполнить запрос
            self.cursor.execute("SELECT id, site_url FROM sites")
            rows = self.cursor.fetchall()

            # Преобразование в словарь
            name_description_dict = {row[0]: row[1] for row in rows}

            return name_description_dict
        except Exception as e:
            print(f"Ошибка при загрузке топиков: {e}")
            return {}


    def topic_id_to_site_id(self):
        """
        Получить словарь topic_id -> [site_id]
        """
        try:
            # Убедиться, что соединение активно
            if not self.connection:
                self.connect()
    
            # Выполнить запрос для получения связи topic_id -> site_id
            self.cursor.execute("""
                SELECT topic_id, id
                FROM sites;
            """)
            rows = self.cursor.fetchall()
    
            # Построить словарь
            topic_to_site = {}
            for topic_id, site_id in rows:
                if topic_id not in topic_to_site:
                    topic_to_site[topic_id] = []
                topic_to_site[topic_id].append(site_id)
    
            return topic_to_site
    
        except Exception as e:
            print(f"Ошибка при создании словаря topic_id -> site_id: {e}")
            return {}
