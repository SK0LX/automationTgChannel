from typing import Dict
import pytest
from unittest.mock import MagicMock, patch, Mock, call

from sqlalchemy import create_engine

from DataBase import DatabaseHandlerORM, Base, VisitedPost, Topic, Prompt, Site
from IRssClient import RssClient
from core import DataBase
from core.IAiClient import IAiClient, OpenRouterClient
from core.IDataBase import IDataBase
from core.IJobRunner import JobRunner
from core.IPostGenerator import PostGenerator
from core.Post_object import Post


@pytest.fixture
def mock_db():
    """Фикстура для мокнутой базы данных."""
    db = MagicMock()
    db.load_visited_posts.return_value = ["http://visited.com"]
    db.add_visited_post = MagicMock()
    return db


@pytest.fixture
def rss_client(mock_db):
    """Фикстура для создания экземпляра RssClient с мокнутой базой данных."""
    return RssClient(db=mock_db)


class MockDatabase(IDataBase):
    """Мок для базы данных."""

    def __init__(self):
        self.visited_posts = []

    def close(self) -> None:
        pass

    def add_post(self, content: str, source: str, topic_id: int, group_id: int) -> None:
        pass

    def load_topics_to_groups(self) -> Dict[int, int]:
        pass

    def load_prompts(self) -> Dict[int, str]:
        pass

    def load_sites(self) -> Dict[int, str]:
        pass

    def site_id_to_topic_id(self) -> Dict[int, int]:
        pass

    def connect(self) -> None:
        pass

    def load_visited_posts(self):
        return self.visited_posts

    def add_visited_post(self, url):
        self.visited_posts.append(url)


def test_rss_client_with_habr():
    """Тест RssClient с использованием реального RSS-канала."""
    rss_url = "https://habr.com/ru/rss/articles/"

    mock_db = MockDatabase()

    rss_client = RssClient(db=mock_db)

    try:
        posts = rss_client.get_posts(rss_url, count=5)

        assert isinstance(posts, list)
        assert len(posts) > 0

        for post in posts:
            assert hasattr(post, "content"), "У объекта отсутствует атрибут 'content'"
            assert hasattr(post, "link"), "У объекта отсутствует атрибут 'link'"
            assert isinstance(post.content, str) and len(post.content) > 0
            assert isinstance(post.link, str) and len(post.link) > 0

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

    assert len(posts) == 0
    rss_client.db.add_visited_post.assert_not_called()


class FakeAiClient(IAiClient):
    """Фейковый AI клиент для тестирования."""

    def send_message(self, model: str, message: str) -> str:
        if "Post content 1" in message:
            return "Summary for Post content 1"
        elif "Post content 2" in message:
            return "Summary for Post content 2"
        elif "Post content 3" in message:
            return "Summary for Post content 3"
        return None


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

    summaries = post_generator.generate(posts=sample_posts, model=model, site_id=site_id)

    assert len(summaries) == len(sample_posts)

    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[2].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_generate_ignores_invalid_summaries(post_generator, sample_posts):
    """Тест, проверяющий, что невалидные сводки игнорируются."""
    model = "test-model"
    site_id = 1

    sample_posts[0].content = "Invalid content" 

    summaries = post_generator.generate(posts=sample_posts, model=model, site_id=site_id)

    assert len(summaries) == 2

    # Проверяем содержимое summary для валидных постов
    assert summaries[0].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[1].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_simple_summary_limited_posts(post_generator, sample_posts):
    """Тест, проверяющий создание кратких версий с ограничением количества постов."""
    model = "test-model"
    site_id = 1
    count = 2

    summaries = post_generator.simple_summary(posts=sample_posts, model=model, count=count, site_id=site_id)

    assert len(summaries) == 2

    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


def test_simple_summary_all_posts(post_generator, sample_posts):
    """Тест, проверяющий создание кратких версий для всех постов."""
    model = "test-model"
    site_id = 1
    count = 5 

    summaries = post_generator.simple_summary(posts=sample_posts, model=model, count=count, site_id=site_id)
    assert len(summaries) == len(sample_posts)
    assert summaries[0].summary == "Summary for Post content 1\nИсточник: http://example.com/1"
    assert summaries[1].summary == "Summary for Post content 2\nИсточник: http://example.com/2"
    assert summaries[2].summary == "Summary for Post content 3\nИсточник: http://example.com/3"


TEST_DB_URL = "sqlite:///:memory:" 


@pytest.fixture(scope="function")
def db_handler():
    class TestDatabaseHandler(DatabaseHandlerORM):
        def connect(self):
            """Пустая реализация метода connect."""
            return self.Session()

        def close(self):
            """Пустая реализация метода close."""
            self.engine.dispose()

    engine = create_engine(TEST_DB_URL)
    Base.metadata.create_all(engine) 
    handler = TestDatabaseHandler(TEST_DB_URL)
    yield handler
    Base.metadata.drop_all(engine)


def test_add_post(db_handler):
    """Тест добавления поста."""
    db_handler.add_post("Test Content", "http://example.com", topic_id=1, group_id=1)

    with db_handler.Session() as session:
        post = session.query(DataBase.Post).first() 
        assert post is not None
        assert post.content == "Test Content"
        assert post.source == "http://example.com"
        assert post.topic_id == 1
        assert post.group_id == 1


def test_add_visited_post(db_handler):
    """Тест добавления посещённого поста."""
    url = "http://example.com/visited"
    db_handler.add_visited_post(url)

    with db_handler.Session() as session:
        visited_post = session.query(VisitedPost).first()
        assert visited_post is not None
        assert visited_post.url == url


def test_load_visited_posts(db_handler):
    """Тест загрузки посещённых постов."""
    urls = ["http://example.com/visited1", "http://example.com/visited2"]
    with db_handler.Session() as session:
        for url in urls:
            session.add(VisitedPost(url=url))
        session.commit()

    loaded_urls = db_handler.load_visited_posts()
    assert set(loaded_urls) == set(urls)


def test_load_topics_to_groups(db_handler):
    """Тест загрузки тем и их групп."""
    with db_handler.Session() as session:
        session.add_all([
            Topic(group_id=10),
            Topic(group_id=20),
        ])
        session.commit()

    topics = db_handler.load_topics_to_groups()
    assert len(topics) == 2
    assert topics[1] == 10
    assert topics[2] == 20


def test_load_prompts(db_handler):
    """Тест загрузки подсказок."""
    with db_handler.Session() as session:
        session.add_all([
            Prompt(site_id=1, prompt_text="Prompt Text 1"),
            Prompt(site_id=2, prompt_text="Prompt Text 2"),
        ])
        session.commit()

    prompts = db_handler.load_prompts()
    assert len(prompts) == 2
    assert prompts[1] == "Prompt Text 1"
    assert prompts[2] == "Prompt Text 2"


def test_load_sites(db_handler):
    """Тест загрузки сайтов."""
    with db_handler.Session() as session:
        session.add_all([
            Site(site_url="http://example1.com", topic_id=100),
            Site(site_url="http://example2.com", topic_id=200),
        ])
        session.commit()

    sites = db_handler.load_sites()
    assert len(sites) == 2
    assert sites[1] == "http://example1.com"
    assert sites[2] == "http://example2.com"


def test_site_id_to_topic_id(db_handler):
    """Тест соответствий site_id -> topic_id."""
    with db_handler.Session() as session:
        session.add_all([
            Site(site_url="http://example1.com", topic_id=1),
            Site(site_url="http://example2.com", topic_id=2),
        ])
        session.commit()

    mapping = db_handler.site_id_to_topic_id()
    assert len(mapping) == 2
    assert mapping[1] == 1
    assert mapping[2] == 2


@pytest.fixture
def mock_db():
    """Мок для базы данных."""
    db = Mock()
    db.load_topics_to_groups.return_value = {1: 10, 2: 20}
    db.load_prompts.return_value = {1: "Prompt 1", 2: "Prompt 2"}
    db.load_sites.return_value = {1: "http://site1.com", 2: "http://site2.com"}
    db.site_id_to_topic_id.return_value = {1: 1, 2: 2}
    return db


@pytest.fixture
def mock_rss_client():
    """Мок для RSS клиента."""
    rss_client = Mock()
    rss_client.get_posts.return_value = [
        {"link": "http://example.com/post1", "content": "Content 1"},
        {"link": "http://example.com/post2", "content": "Content 2"},
    ]
    return rss_client


@pytest.fixture
def mock_post_generator():
    """Мок для генератора постов."""
    post_generator = Mock()
    post_generator.simple_summary.return_value = [
        Mock(summary="Summary 1", link="http://example.com/post1"),
        Mock(summary="Summary 2", link="http://example.com/post2"),
    ]
    return post_generator


@pytest.fixture
def job_runner(mock_rss_client, mock_post_generator, mock_db):
    """Инициализация JobRunner с моками."""
    return JobRunner(rss_client=mock_rss_client, post_generator=mock_post_generator, db=mock_db)


def test_run(job_runner, mock_db, mock_rss_client, mock_post_generator):
    """Тест метода run."""
    job_runner.run(count=2, model="test_model")

    # Проверяем, что база обновилась
    mock_db.load_sites.assert_called()
    mock_db.site_id_to_topic_id.assert_called()

    mock_rss_client.get_posts.assert_has_calls([
        call("http://site1.com", 2),
        call("http://site2.com", 2),
    ])

    mock_post_generator.simple_summary.assert_has_calls([
        call(posts=mock_rss_client.get_posts.return_value, model="test_model", count=2, site_id=1),
        call(posts=mock_rss_client.get_posts.return_value, model="test_model", count=2, site_id=2),
    ])

    mock_db.add_post.assert_has_calls([
        call("Summary 1", "http://example.com/post1", topic_id=1, group_id=10),
        call("Summary 2", "http://example.com/post2", topic_id=1, group_id=10),
        call("Summary 1", "http://example.com/post1", topic_id=2, group_id=20),
        call("Summary 2", "http://example.com/post2", topic_id=2, group_id=20),
    ], any_order=True)


def test_update_db(job_runner, mock_db):
    """Тест метода update_db."""
    mock_db.reset_mock()

    job_runner.update_db()

    try:
        mock_db.load_sites.assert_called_once()
        mock_db.site_id_to_topic_id.assert_called_once()
    except AssertionError:
        print("Вызовы мока load_sites:")
        print(mock_db.load_sites.mock_calls)
        print("Вызовы мока site_id_to_topic_id:")
        print(mock_db.site_id_to_topic_id.mock_calls)
        raise


@pytest.fixture
def mock_api_key():
    """Фикстура для мок-ключа API."""
    return "test_api_key"


@pytest.fixture
def client(mock_api_key):
    """Создаём экземпляр OpenRouterClient."""
    return OpenRouterClient(api_key=mock_api_key)


@patch("requests.post")
def test_send_message_success(mock_post, client):
    """Тест успешного ответа API."""
    # Настройка мока ответа API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": "Test AI Response"}}
        ]
    }
    mock_post.return_value = mock_response

    model = "test-model"
    message = "Hello, AI!"
    response = client.send_message(model, message)

    assert response == "Test AI Response"

    mock_post.assert_called_once_with(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer test_api_key"},
        data='{"model": "test-model", "messages": [{"role": "user", "content": "Hello, AI!"}]}'
    )


@patch("requests.post")
def test_send_message_api_error(mock_post, client):
    """Тест обработки ошибки API (не 200 статус код)."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        client.send_message("test-model", "Hello, AI!")

    assert "Ошибка API: 400, Bad Request" in str(exc_info.value)

    mock_post.assert_called_once()


@patch("requests.post")
def test_send_message_unexpected_response(mock_post, client):
    """Тест обработки некорректного формата ответа API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}  # Пустой JSON
    mock_post.return_value = mock_response

    with pytest.raises(KeyError):
        client.send_message("test-model", "Hello, AI!")

    mock_post.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
