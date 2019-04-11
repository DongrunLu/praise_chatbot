from tqdm import tqdm
from data_loader import DataLoader
from es_model.es_type import DoubanQAType, DoubanContentType
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


def save_to_es(model_type, pair_id, question, answer, post_content):
    praise = model_type()
    praise_question = question
    praise_answer = answer
    praise.meta.id = pair_id
    praise.question = praise_question
    praise.answer = praise_answer
    praise.content = post_content

    praise.save()


post_corpus_path = '../data/douban_post.json'
comment_corpus_path = '../data/douban_comment.json'

data_loader = DataLoader()
post_corpus, _, _, praise_corpus = data_loader.get_total_corpus(
    post_corpus_path = post_corpus_path,
    comment_corpus_path = comment_corpus_path
)


for pair_id, content in tqdm(praise_corpus.items(), desc="Writing into ES..."):
    question = content['question']
    answer = content['answer']
    post_content = post_corpus[content['post_id']]['post_content']
    save_to_es(DoubanContentType, pair_id, question, answer, post_content)
