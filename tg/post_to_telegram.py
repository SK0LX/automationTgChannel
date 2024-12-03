import time
import psycopg2
import telebot
from dotenv import load_dotenv
import os

# Загрузка переменных из .env
load_dotenv()

# Настройки базы данных из .env
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost',  # Или замените на другой хост, если нужно
    'port': 5432          # Убедитесь, что порт совпадает с вашим PostgreSQL
}

# Настройки Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Добавьте этот параметр в .env
bot = telebot.TeleBot(TELEGRAM_TOKEN)


def fetch_accepted_posts():
    """Получает все принятые посты из базы данных."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = """
    SELECT p.id, p.content, t.channel_id 
    FROM posts p
    JOIN topics tp ON p.topic_id = tp.id
    JOIN telegram_channels t ON t.topic_id = tp.id
    WHERE p.is_accepted = true;
    """
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return posts


def delete_post_after_sending(post_id):
    """Удаляет пост из базы данных после отправки."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    query = "DELETE FROM posts WHERE id = %s;"
    cursor.execute(query, (post_id,))
    conn.commit()
    cursor.close()
    conn.close()


def post_to_telegram(content, channel_id):
    """Отправляет сообщение в указанный Telegram-канал."""
    try:
        bot.send_message(chat_id=channel_id, text=content)
        print(f"Успешно отправлено в канал {channel_id}")
    except Exception as e:
        print(f"Ошибка отправки в канал {channel_id}: {e}")


def main():
    """Основная логика обработки постов."""
    while True:
        print("Проверка новых постов...")
        posts = fetch_accepted_posts()
        for post_id, content, channel_id in posts:
            post_to_telegram(content, channel_id)
            delete_post_after_sending(post_id)
        print("Ожидание...")
        time.sleep(40)


if __name__ == "__main__":
    main()
