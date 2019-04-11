import numpy as np
import jieba
from tqdm import tqdm
from gensim import similarities
from gensim.corpora import Dictionary
from gensim import models
from pprint import pprint

class SimModel():
    """Similarity model, contains 'tf-idf', 'lda', 'lsi'"""
    def __init__(self, model_type="tf-idf"):
        self._model_type = model_type.lower()
        self._model_mapping = {
            "tf-idf": self.tf_idf_model,
            "lda": self.ida_model,
            "lsi": self.lsi_model,
        }
        self._sim_model = None
        self._corpus_sim = None
        self._index = None
        self._stopwords = ['的', '吗', '我', '会', '使用', '跟', '了', '有', '什么', '这个', '下', '或者', '能', '要', '怎么', '呢', '吧',
                           '都']  # 取出停用词
        self._dictionary = None
        self._train = None

    def get_dict(self, corpus):
        sentences = [list(jieba.cut(sentence)) for sentence in corpus]
        train = [[token for token in sentence if token not in self._stopwords] for sentence in sentences]
        dictionary = Dictionary(train)
        self._dictionary = dictionary
        self._train = train
        return dictionary, train

    def train_model(self, train, dictionary):
        corpus = [dictionary.doc2bow(text) for text in tqdm(train, desc="Processing corpus")]
        self._sim_model = self._model_mapping[self._model_type](corpus, dictionary)
        self._corpus_sim = self._sim_model[corpus]
        self._index = similarities.MatrixSimilarity(self._corpus_sim)
        self._sim_model.save('%s.model' % self._model_type)

    def tf_idf_model(self, corpus, *args):
        return models.TfidfModel(corpus)

    def ida_model(self, corpus, dictionary):
        return models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=10)

    def lsi_model(self, corpus, dictionary):
        return models.LsiModel(corpus, id2word=dictionary, num_topics=10)

    def load_sentence_tf_idf(self, line):
        tokens = list(jieba.cut(line))
        sentence_bow = self._dictionary.doc2bow(tokens)
        sentence_tf_idf = self._sim_model[sentence_bow]
        return sentence_tf_idf

    def get_vec(self, doc_bow):
        return [i[1] for i in doc_bow]

    def _sim(self, vec1, vec2):
        padding_num = len(vec1) - len(vec2)
        if padding_num >= 0:
            longer, shorter = vec1, vec2
        else:
            longer, shorter = vec2, vec1
        shorter = shorter + [0 for _ in range(abs(padding_num))]
        try:
            sim = np.dot(longer, shorter) / (np.linalg.norm(longer) * np.linalg.norm(shorter))
        except ValueError:
            sim = 0
        return sim

    def _calculate_sim(self, sentence, k):
        sentence_tfidf = self.load_sentence_tf_idf(sentence)
        sentence_sims = self._index[sentence_tfidf]
        sorted_sentence_sims = sorted(enumerate(sentence_sims), key=lambda item: -item[1])
        return sorted_sentence_sims

    def _calculate_sim2(self, sentence, k):
        sentence_tfidf = self.load_sentence_tf_idf(sentence)
        sentence_sims = {i: self._sim(self.get_vec(sentence_tfidf), self.get_vec(corpus_sentence))
                         for i, corpus_sentence in tqdm(enumerate(self._corpus_sim), desc="Calculate sim")}
        sorted_sentence_sims = sorted(sentence_sims.items(), key=lambda item: item[1], reverse=True)
        return sorted_sentence_sims

    def return_top_k_title(self, sentence, corpus, k):
        sorted_sentence_sims = self._calculate_sim(sentence, k)
        coupus_titles = [corpus[doc_idx] for doc_idx, sim_value in sorted_sentence_sims]
        return coupus_titles

    def return_top_k_index(self, sentence, k):
        sorted_sentence_sims = self._calculate_sim(sentence, k)
        topk_idx = [(doc_idx, sim_value) for doc_idx, sim_value in sorted_sentence_sims[:k]]
        return topk_idx

def return_top_k(coupus_titles, k):
    topk = [coupus_title for coupus_title in coupus_titles if len(coupus_title) > 10]
    return topk[:k]

def main():
    from data_loader import DataLoader
    post_corpus_path = './data/douban_post.json'
    comment_corpus_path = './data/douban_comment.json'

    # load data
    data_loader = DataLoader()
    post_corpus, comment_corpus, reply_corpus, praise_corpus = data_loader.get_total_corpus(
        post_corpus_path=post_corpus_path,
        comment_corpus_path=comment_corpus_path
    )
    raw_praise_corpus = [[content['question'], content['answer']] for idx, content in praise_corpus.items()]

    # build similarity model
    model = SimModel("tf-idf")
    dictionary, train = model.get_dict(raw_praise_corpus)
    model.train_model(train, dictionary)

    # request response
    test_query = "我留了胡子"
    res_title = model.return_top_k_title(test_query, raw_praise_corpus, 20)
    pprint(res_title[:10])

if __name__ == '__main__':
    main()