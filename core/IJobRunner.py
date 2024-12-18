import time

from core.IDataBase import IDataBase
from core.IPostGenerator import IPostGenerator
from core.IRssClient import IRssClient


class JobRunner:
    def __init__(self, rss_client: IRssClient, post_generator: IPostGenerator, db: IDataBase):
        self.rss_client = rss_client
        self.post_generator = post_generator
        self.db = db
        self.topics = self.db.load_topics_to_groups()
        self.prompts = self.db.load_prompts()
        self.sites = self.db.load_sites()
        self.site_id_to_topic_id = self.db.site_id_to_topic_id()

    def run(self, count: int, model: str):
        self.update_db()
        for site_id, site_url in self.sites.items():
            posts = self.rss_client.get_posts(site_url, count)
            summaries = self.post_generator.simple_summary(posts=posts, model=model, count=count, site_id=site_id)
            time.sleep(10)
            for summary in summaries:
                self.db.add_post(summary.summary, summary.link, topic_id=self.site_id_to_topic_id[site_id],
                                 group_id=self.topics[self.site_id_to_topic_id[site_id]])

    def update_db(self):
        self.sites = self.db.load_sites()
        self.site_id_to_topic_id = self.db.site_id_to_topic_id()