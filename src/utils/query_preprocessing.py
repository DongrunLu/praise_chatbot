import jieba
# import synonyms
from pprint import pprint


def query_preprocessing(query):
    tokens = list(jieba.cut(query))

    # total_words = synonym_expand(tokens)  # expand synonym
    total_words = tokens
    print("Query:")
    pprint(total_words)
    return " ".join(total_words)


def synonym_expand(tokens):
    total_words = []
    for token in tokens:
        nearby_words = synonyms.nearby(token)[0]
        nearby_scores = synonyms.nearby(token)[1]
        if len(nearby_words) > 1 and nearby_scores[1] > 0.9:
            total_words.append(nearby_words[1])
    total_words += tokens
    return total_words
