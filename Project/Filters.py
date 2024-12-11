import re
from typing import List

from fuzzywuzzy import fuzz

import Post_object


class Filters:
    def filter_posts_by_keywords(self, posts, keywords):
        """
          Фильтрует список постов по ключевым словам с учётом разных форм слова.
          Args:
            posts (list): Список постов для фильтрации.
            keywords (list): Список ключевых слов для фильтрации.
          Returns:
            list: Отфильтрованный список постов, содержащих слова из ключевых слов.
          """
        filtered_posts = []
        for post in posts:
            if any(re.search(rf'\b{keyword}', post, re.IGNORECASE) for keyword in keywords):
                filtered_posts.append(post)

        return filtered_posts

    def filter_posts_by_hashtags(self, posts, hashtags=None) -> List[Post_object]:
        """
          Фильтрует список постов по хэштегам с учётом неточного совпадения(Левейнштейн).
          Args:
            posts (list): Список Post_object для фильтрации.
            hashtags (list): Список хэштегов для фильтрации.
          Returns:
            list: Отфильтрованный список постов, содержащих похожие хэштеги.
        """
        if hashtags is None:
            return posts
        filtered_posts = []
        for post in posts:
            hashtags_in_post = post.content.split("#")[1::]
            for hashtag in hashtags:
                for post_hashtag in hashtags_in_post:
                    # Проверяем расстояние Левенштейна для каждого хэштега
                    if fuzz.ratio(hashtag, post_hashtag) >= 60:
                        filtered_posts.append(post)
                        break
                if post in filtered_posts:
                    break
        return filtered_posts
