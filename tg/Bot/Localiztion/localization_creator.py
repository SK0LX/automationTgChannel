import json

data = {
    "to_menu": "В главное меню",
    "moderate": "Модерировать посты",
    "continue": "Продолжить модерацию",
    "accept": "Принять пост",
    "decline": "Отклонить пост",
    "greet": "Привет! Выбери тему постов:",
    "chose": "Вы выбрали тему ",
    "restricted": "Эта команда доступна только администраторам.",
    "no_topic": "Тема постов не выбрана",
    "contents": "Содержание поста: ",
    "no_posts": "Нет доступных постов для модерации.",
    "post_accepted": "Пост принят!",
    "post_declined": "Пост отклонён!"
}

file_path = "ru.json"

with open(file_path, "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Данные сохранены в файл {file_path}")
