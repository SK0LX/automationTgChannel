from abc import ABC, abstractmethod
from typing import Dict, List


class IDataBase(ABC):
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def add_post(self, content: str, source: str, topic_id: int, group_id:int) -> None:
        pass

    @abstractmethod
    def load_topics_to_groups(self) -> Dict[int, int]:
        pass

    @abstractmethod
    def load_prompts(self) -> Dict[int, str]:
        pass

    @abstractmethod
    def load_sites(self) -> Dict[int, str]:
        pass

    @abstractmethod
    def site_id_to_topic_id(self) -> Dict[int, int]:
        pass

    @abstractmethod
    def add_visited_post(self, url: str) -> None:
        pass

    @abstractmethod
    def load_visited_posts(self) -> List[str]:
        pass
