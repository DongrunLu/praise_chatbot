from elasticsearch_dsl import DocType, Text, Keyword
from elasticsearch_dsl.connections import connections

class DoubanQAType(DocType):
    praise_id = Keyword()
    question = Text(analyzer="ik_max_word")
    answer = Text(analyzer="ik_max_word")

    class Meta:
        index = "douban_qa_corpus"
        doc_type = "praise"

    def save_to_es(self, pair_id, question, answer, *args):
        praise = DoubanContentType()
        praise_question = question
        praise_answer = answer
        praise.meta.id = pair_id
        praise.question = praise_question
        praise.answer = praise_answer

        praise.save()

class DoubanContentType(DocType):
    praise_id = Keyword()
    question = Text(analyzer="ik_max_word")
    answer = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "douban_qa_content_corpus"
        doc_type = "praise"

if __name__ == "__main__":
    connections.create_connection(hosts=["localhost"])
    DoubanContentType.init()