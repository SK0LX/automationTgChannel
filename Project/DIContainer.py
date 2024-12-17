import time
import yaml
import schedule
from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

import DataBase
from IAiClient import OpenRouterClient
from IJobRunner import JobRunner
from IPostGenerator import PostGenerator
from IRssClient import RssClient


class AppContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    with open("config.yaml", "r", encoding="utf-8-sig") as config_file:
        config_data = yaml.safe_load(config_file)

    connection_string = providers.Object(
        f"postgresql://{config_data['db']['user']}:"
        f"{config_data['db']['password']}@"
        f"{config_data['db']['host']}/"
        f"{config_data['db']['database']}"
    )

    engine = providers.Singleton(
        create_engine,
        connection_string,
        pool_pre_ping=True,
    )

    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine,
        expire_on_commit=False,
    )

    scoped_session = providers.Singleton(
        scoped_session,
        session_factory,
    )

    # Database Handler с использованием сессии
    database_handler = providers.Factory(
        DataBase.DatabaseHandlerORM,
        db_url=connection_string
    )

    # AI Client
    ai_client = providers.Singleton(OpenRouterClient, api_key=config_data["api"]["ai_key"])

    # Post Generator
    post_generator = providers.Singleton(
        PostGenerator,
        ai_client=ai_client,
        prompts=providers.Callable(lambda: AppContainer.database_handler().load_prompts()),
    )

    # RSS Client
    rss_client = providers.Singleton(
        RssClient,
        db=database_handler,
    )

    # Job Runner
    job_runner = providers.Singleton(
        JobRunner,
        rss_client=rss_client,
        post_generator=post_generator,
        db=database_handler,
    )


if __name__ == "__main__":
    container = AppContainer()

    # Получение задания из контейнера
    job = container.job_runner()

    # Планирование работы
    schedule.every(1).seconds.do(job.run, 1, "meta-llama/llama-3.2-3b-instruct:free")

    # Основной цикл
    while True:
        schedule.run_pending()
        time.sleep(1)
