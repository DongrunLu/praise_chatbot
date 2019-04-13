import json
from pprint import pprint
from w3lib.html import remove_tags
from collections import defaultdict


class DataLoader():
    def __init__(self):
        self._praise_filter_word_set = ('夸夸群', '辱骂群', '吗')
        self._comment_filter_word_set = ('该条回应已被删除')

    def _replace_words(self, comment_content):
        comment_content = comment_content.replace("楼主", "你")
        comment_content = comment_content.replace("lz", "")
        comment_content = comment_content.replace("$$$$$$$", "")
        return comment_content

    def _contains_filter_words(self, content, filter_words):
        return True if any(str_ in content for str_ in filter_words) else False

    def load_corpus(self, json_path):
        """Loads corpus from loacal"""
        with open(json_path, 'r', encoding="utf-8") as f:
            items = json.load(f)
            items = items['RECORDS']

        return items

    def get_post_corpus(self, post_items):
        """Gets post corpus, contains title, author, etc."""
        post_dict = defaultdict(lambda: {})
        for post_item in post_items:
            post_id = post_item['post_id']
            post_title = post_item['post_title']
            post_author_url = post_item['post_author_url']
            post_content = post_item['post_content']

            post_dict[post_id]['post_author_url'] = post_author_url
            post_dict[post_id]['post_title'] = post_title
            post_dict[post_id]['post_content'] = remove_tags(post_content).strip()

        return post_dict

    def get_reply_corpus(self, comment_items):
        """Gets reply corpus, contains pair of original comment content and reply"""
        reply_corpus = {}
        for comment_item in comment_items:
            comment_reply_flag = comment_item['comment_reply_flag']
            if comment_reply_flag == "1":
                comment_reply_org_content = comment_item["comment_reply_org_content"]
                if self._contains_filter_words(comment_reply_org_content, self._comment_filter_word_set):
                    continue
                comment_content = comment_item['comment_content']
                comment_id = comment_item['comment_id']

                reply_corpus[comment_id] = {
                    "org_content": self._replace_words(comment_reply_org_content),
                    "reply": self._replace_words(comment_content)
                }

        return reply_corpus


    def get_comment_corpus(self, comment_items, post_corpus):
        """Gets comment corpus, contains post id, comment author, comment content, etc."""
        comment_dict = {}
        for comment_item in comment_items:
            comment_id = comment_item['comment_id']
            comment_author_url = comment_item['comment_author_url']
            comment_reply_flag = comment_item['comment_reply_flag']
            comment_content = comment_item['comment_content']
            post_id = comment_item['post_id']
            post_author_url = post_corpus[post_id].get('post_author_url', "")
            if post_author_url == comment_author_url:
                continue
            if comment_reply_flag == "1":
                continue

            if self._contains_filter_words(comment_content, self._praise_filter_word_set):
                continue
            comment_dict.setdefault(post_id, [])
            comment_dict[post_id].append({
                "comment_id": comment_id,
                "comment_content": self._replace_words(comment_content)
                }
            )
        return comment_dict


    def get_praise_corpus(self, post_corpus, comment_corpus):
        """Gets praise corpus from post_corpus and comment_corpus, contains the pair of question and praise"""
        praise_corpus = {}
        for post_id in comment_corpus:
            question = post_corpus[post_id]['post_title']
            answers = comment_corpus[post_id]
            for answer in answers:
                praise_corpus[answer['comment_id']] = {
                    "question": question,
                    "answer": answer['comment_content'],
                    'post_id': post_id
                }
        return praise_corpus

    def get_total_corpus(self, post_corpus_path, comment_corpus_path):
        post_items = self.load_corpus(post_corpus_path)
        comment_items = self.load_corpus(comment_corpus_path)

        post_corpus = self.get_post_corpus(post_items)
        comment_corpus = self.get_comment_corpus(comment_items, post_corpus)
        reply_corpus = self.get_reply_corpus(comment_items)
        praise_corpus = self.get_praise_corpus(post_corpus, comment_corpus)

        return post_corpus, comment_corpus, reply_corpus, praise_corpus


if __name__ == '__main__':
    post_corpus_path = './data/douban_post.json'
    comment_corpus_path = './data/douban_comment.json'

    data_loader = DataLoader()
    post_corpus, comment_corpus, reply_corpus, praise_corpus = data_loader.get_total_corpus(
        post_corpus_path = post_corpus_path,
        comment_corpus_path = comment_corpus_path
    )

    print("SIZE OF REPLY CORPUS: %s" % len(reply_corpus))
    print("REPLY CORPUS SAMPLE:")
    pprint([(idx, content) for idx, content in reply_corpus.items()][500:505])

    print("SIZE OF PRAISE CORPUS: %s" % len(praise_corpus))
    print("PRAISE CORPUS SAMPLE:")
    pprint([(idx, content) for idx, content in praise_corpus.items()][500:505])