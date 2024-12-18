from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, InstrumentedAttribute

from IDataBase import IDataBase

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    source = Column(String, nullable=False)
    is_accepted = Column(Boolean, default=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    group_id = Column(Integer, nullable=False)


class VisitedPost(Base):
    __tablename__ = "visitedposts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, nullable=False)


class Prompt(Base):
    __tablename__ = "prompts"
    site_id = Column(Integer, primary_key=True)
    prompt_text = Column(String, nullable=False)



class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, autoincrement=True)
    site_url = Column(String, nullable=False)
    topic_id = Column(Integer, nullable=False)


class DatabaseHandlerORM(IDataBase):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def add_post(self, content: str, source: str, topic_id: int, group_id: int) -> None:
        session = self.Session()
        try:
            post = Post(content=content, source=source, topic_id=topic_id, group_id=group_id)
            session.add(post)
            session.commit()
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Ошибка добавления поста: {e}")
        finally:
            session.close()

    def add_visited_post(self, url: str) -> None:
        session = self.Session()
        try:
            visited_post = VisitedPost(url=url)
            session.add(visited_post)
            session.commit()
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Ошибка добавления посещенного поста: {e}")
        finally:
            session.close()

    def load_visited_posts(self) -> list[InstrumentedAttribute]:
        session = self.Session()
        try:
            posts = session.query(VisitedPost).all()
            return [post.url for post in posts]
        finally:
            session.close()

    def load_topics_to_groups(self) -> dict[InstrumentedAttribute, InstrumentedAttribute]:
        session = self.Session()
        try:
            topics = session.query(Topic).all()
            return {topic.id: topic.group_id for topic in topics}
        finally:
            session.close()

    def load_prompts(self) -> dict[InstrumentedAttribute, InstrumentedAttribute]:
        session = self.Session()
        try:
            prompts = session.query(Prompt).all()
            return {prompt.site_id: prompt.prompt_text for prompt in prompts}
        finally:
            session.close()

    def load_sites(self) -> dict[InstrumentedAttribute, InstrumentedAttribute]:
        session = self.Session()
        try:
            sites = session.query(Site).all()
            return {site.id: site.site_url for site in sites}
        finally:
            session.close()

    def site_id_to_topic_id(self) -> dict[InstrumentedAttribute, InstrumentedAttribute]:
        session = self.Session()
        try:
            sites = session.query(Site).all()
            return {site.id: site.topic_id for site in sites}
        finally:
            session.close()
