import pytest
from unittest.mock import MagicMock, patch
from DataBase import DatabaseHandlerORM
from IRssClient import RssClient


@pytest.fixture
def mock_db():
    """Фикстура для мокнутой базы данных."""
    db = MagicMock()
    db.load_visited_posts.return_value = ["http://visited.com"]  # Посты, которые уже были посещены
    db.add_visited_post = MagicMock()  # Для проверки, добавляется ли новый пост
    return db


@pytest.fixture
def rss_client(mock_db):
    """Фикстура для создания экземпляра RssClient с мокнутой базой данных."""
    return RssClient(db=mock_db)


class MockDatabase:
    """Мок для базы данных."""
    def __init__(self):
        self.visited_posts = []

    def load_visited_posts(self):
        return self.visited_posts

    def add_visited_post(self, url):
        self.visited_posts.append(url)


def test_rss_client_with_habr():
    """Тест RssClient с использованием реального RSS-канала."""
    # URL реального RSS-канала
    rss_url = "https://habr.com/ru/rss/articles/"

    # Мок базы данных
    mock_db = MockDatabase()

    # Создаем экземпляр RssClient
    rss_client = RssClient(db=mock_db)

    try:
        # Получаем посты
        posts = rss_client.get_posts(rss_url, count=5)

        # Проверяем, что возвращается список
        assert isinstance(posts, list)
        assert len(posts) > 0  # Убедитесь, что есть хотя бы один пост

        for post in posts:
            # Проверяем, что каждый пост имеет необходимые атрибуты
            assert isinstance(post, Post)
            assert isinstance(post.content, str) and len(post.content) > 0
            assert isinstance(post.link, str) and len(post.link) > 0

            # Проверяем, что ссылки добавляются в список посещенных
            assert post.link in mock_db.load_visited_posts()

        print("Тест прошел успешно: Все посты корректны.")
    except Exception as e:
        pytest.fail(f"Тест завершился ошибкой: {e}")


@patch("feedparser.parse")
def test_get_posts_bozo_error(mock_parse, rss_client):
    """Тест обработки ошибки RSS."""
    mock_parse.return_value = MagicMock(
        bozo=True,
        bozo_exception=ValueError("Invalid RSS feed")
    )

    posts = rss_client.get_posts("http://example.com/rss", count=2)

    # Проверяем, что ничего не возвращается при ошибке
    assert len(posts) == 0


@patch("feedparser.parse")
def test_get_posts_no_date(mock_parse, rss_client):
    """Тест обработки постов без даты публикации."""
    mock_parse.return_value = MagicMock(
        bozo=False,
        entries=[
            {
                "title": "No Date Post",
                "summary": "<p>No Date Summary</p>",
                "link": "http://example.com/nodate",
            },
        ],
    )

    posts = rss_client.get_posts("http://example.com/rss", count=1)

    # Проверяем, что посты без даты публикации пропускаются
    assert len(posts) == 0
    rss_client.db.add_visited_post.assert_not_called()

import pytest
from IPostGenerator import PostGenerator
from Post_object import Post
from IAiClient import IAiClient


class FakeAiClient(IAiClient):
    """Фейковый AI клиент для тестирования."""
    def send_message(self, model: str, message: str) -> str:
        if "Post content 1" in message:
            return "Summary for Post content 1"
        elif "Post content 2" in message:
            return "Summary for Post content 2"
        elif "Post content 3" in message:
            return "Summary for Post content 3"
        return None  # Для проверки случаев некорректного ответа


@pytest.fixture
def fake_ai_client():
    """Фикстура для фейкового AI клиента."""
    return FakeAiClient()


@pytest.fixture
def prompts():
    """Фикстура для подсказок."""
    return {
        1: "Summarize this: {}",
        2: "Briefly summarize: {}",
    }


@pytest.fixture
def post_generator(fake_ai_client, prompts):
    """Фикстура для создания экземпляра PostGenerator."""
    return PostGenerator(ai_client=fake_ai_client, prompts=prompts)


@pytest.fixture
def sample_posts():
    """Фикстура для списка тестовых постов."""
    return [
        Post(content="Post content 1", link="http://example.com/1"),
        Post(content="Post content 2", link="http://example.com/2"),
        Post(content="Post content 3", link="http://example.com/3"),
    ]


def test_generate_creates_summaries(post_generator, sample_posts):
    """Тест, проверяющий генерацию сводок для списка постов."""
    model = "test-model"
    site_id = 1

    # Вызываем метод
    summaries = post_generator.generate(posts=sample_posts, model=model, site_id=site_id)

    # Проверяем, что количество сводок соответствует числу постов
    assert len(summaries) == len(sample_posts)

    # Проверяем содержимое summary для каждого поста
    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[2].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_generate_ignores_invalid_summaries(post_generator, sample_posts):
    """Тест, проверяющий, что невалидные сводки игнорируются."""
    model = "test-model"
    site_id = 1

    # Устанавливаем некорректный контент для одного из постов
    sample_posts[0].content = "Invalid content"  # FakeAiClient вернет None для этого контента

    # Вызываем метод
    summaries = post_generator.generate(posts=sample_posts, model=model, site_id=site_id)

    # Проверяем, что только валидные посты возвращены
    assert len(summaries) == 2  # Один пост с некорректным контентом отфильтровался

    # Проверяем содержимое summary для валидных постов
    assert summaries[0].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[1].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_simple_summary_limited_posts(post_generator, sample_posts):
    """Тест, проверяющий создание кратких версий с ограничением количества постов."""
    model = "test-model"
    site_id = 1
    count = 2

    # Вызываем метод
    summaries = post_generator.simple_summary(posts=sample_posts, model=model, count=count, site_id=site_id)

    # Проверяем, что обрабатываются только каждые count-й пост
    assert len(summaries) == 2  # sample_posts[0] и sample_posts[2]

    # Проверяем содержимое summary для выбранных постов
    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_simple_summary_all_posts(post_generator, sample_posts):
    """Тест, проверяющий создание кратких версий для всех постов."""
    model = "test-model"
    site_id = 1
    count = 5  # Больше длины sample_posts

    # Вызываем метод
    summaries = post_generator.simple_summary(posts=sample_posts, model=model, count=count, site_id=site_id)
    # Проверяем, что обрабатываются все посты
    assert len(summaries) == len(sample_posts)

    # Проверяем содержимое summary для каждого поста
    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[2].summary == "Summary for Post content 3\nИсточник: http://example.com/3"

# Конфигурация для тестовой базы данных
TEST_DB_CONFIG = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "Lfybbk_2005"
}


@pytest.fixture
def db_handler():
    """Фикстура для инициализации DatabaseHandler."""
    db = DatabaseHandlerORM(TEST_DB_CONFIG)
    yield db
    db.close()


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Автоматическая очистка перед и после теста."""
    db = DatabaseHandler(TEST_DB_CONFIG)
    db.connect()
    cursor = db.connection.cursor()

    # Очистка таблиц
    cursor.execute("TRUNCATE posts, visitedposts, topics, prompts, sites RESTART IDENTITY CASCADE;")
    db.connection.commit()
    cursor.close()
    db.close()


def test_add_post(db_handler):
    """Тест добавления поста в базу данных."""
    content = "Test Content"
    source = "http://example.com/test"

    # Добавляем тему и сайт
    db_handler.connect()
    db_handler.cursor.execute("INSERT INTO topics (name) VALUES ('Test Topic') RETURNING id;")
    topic_id = db_handler.cursor.fetchone()[0]

    db_handler.cursor.execute("INSERT INTO sites (site_url, topic_id) VALUES ('http://example.com', %s) RETURNING id;",
                              (topic_id,))
    site_id = db_handler.cursor.fetchone()[0]
    db_handler.connection.commit()
    db_handler.close()

    # Добавляем пост
    db_handler.add_post(content, source, topic_id, 1)

    # Проверяем добавление
    db_handler.connect()
    db_handler.cursor.execute("SELECT content, source, is_accepted, topic_id FROM posts;")
    rows = db_handler.cursor.fetchall()
    db_handler.close()

    assert len(rows) == 1
    assert rows[0] == (content, source, False, topic_id)


def test_add_visited_post(db_handler):
    """Тест добавления посещенного поста."""
    url = "http://example.com/visited"
    db_handler.add_visited_post(url)

    # Проверяем добавление
    db_handler.connect()
    db_handler.cursor.execute("SELECT url FROM visitedposts;")
    rows = db_handler.cursor.fetchall()
    db_handler.close()

    assert len(rows) == 1
    assert rows[0][0] == url


def test_load_visited_posts(db_handler):
    """Тест загрузки посещенных постов."""
    urls = ["http://example.com/visited1", "http://example.com/visited2"]

    # Добавляем записи вручную
    db_handler.connect()
    cursor = db_handler.cursor
    cursor.executemany("INSERT INTO visitedposts (url) VALUES (%s);", [(url,) for url in urls])
    db_handler.connection.commit()
    db_handler.close()

    # Проверяем загрузку
    visited_posts = db_handler.load_visited_posts()
    assert visited_posts == urls


def test_load_topics(db_handler):
    """Тест загрузки тем."""
    topics = [("Topic 1",), ("Topic 2",)]

    # Добавляем темы
    db_handler.connect()
    cursor = db_handler.cursor
    cursor.executemany("INSERT INTO topics (name) VALUES (%s);", topics)
    db_handler.connection.commit()
    db_handler.close()

    # Проверяем загрузку
    loaded_topics = db_handler.load_topics_to_grops()
    assert len(loaded_topics) == len(topics)
    for topic_id, group_id in loaded_topics.items():
        assert f"Topic {topic_id}" in [t[0] for t in topics]



def test_load_prompts(db_handler):
    """Тест загрузки подсказок."""
    # Добавляем темы и сайты
    db_handler.connect()
    cursor = db_handler.cursor
    cursor.execute("INSERT INTO topics (name) VALUES ('Topic 1') RETURNING id;")
    topic_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO sites (site_url, topic_id) VALUES ('http://example.com', %s) RETURNING id;",
                   (topic_id,))
    site_id = cursor.fetchone()[0]

    prompts = [(site_id, "Prompt for site 1")]

    # Добавляем подсказки
    cursor.executemany("INSERT INTO prompts (site_id, prompt_text) VALUES (%s, %s);", prompts)
    db_handler.connection.commit()
    db_handler.close()

    # Проверяем загрузку подсказок
    loaded_prompts = db_handler.load_prompts()
    assert len(loaded_prompts) == len(prompts)
    for site_id, prompt_text in prompts:
        assert loaded_prompts[site_id] == prompt_text

if __name__ == "__main__":
    pytest.main([__file__])
    