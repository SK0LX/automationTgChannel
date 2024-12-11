import os
import time
import yaml
import json
import schedule
from dependency_injector import containers, providers

import DataBase
import Parser
from Filters import Filters
from IAiClient import OpenRouterClient
from IJobRunner import JobRunner
from IPostGenerator import PostGenerator
from IRssClient import RssClient


class AppContainer(containers.DeclarativeContainer):
    with open("config.yaml", "r", encoding="utf-8-sig") as config_file:
        config_data = yaml.safe_load(config_file)
    # AI Client
    ai_client = providers.Singleton(OpenRouterClient, api_key=config_data["api"]["ai_key"])

    # Database Handler
    database_handler = providers.Singleton(
        DataBase.DatabaseHandler,
        config=config_data["db"])

    # Post Generator
    post_generator = providers.Singleton(
        PostGenerator,
        ai_client=ai_client,
        prompts=database_handler().load_prompts(),
    )
    
    # RSS Client
    rss_client = providers.Singleton(RssClient, db=database_handler)
    
    # Job Runner
    job_runner = providers.Singleton(
        JobRunner,
        rss_client=rss_client,
        post_generator=post_generator,
        db=database_handler
    )


if __name__ == "__main__":
    container = AppContainer()
    job = container.job_runner()

    schedule.every(1).seconds.do(job.run, 1, "meta-llama/llama-3.2-3b-instruct:free")

    while True:
        schedule.run_pending()
        time.sleep(1)
