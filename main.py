from elasticsearch import Elasticsearch
from query_preprocessing import query_preprocessing
from pprint import pprint


def request_query(query):
    """Requests quert"""
    response = client.search(
        index = "douban_qa_content_corpus",
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["question"]
                }
            },
            "from": 0,
            "size": 10,
        }
    )
    response = [
        {
            "score": res['_score'],
            "question": res['_source']['question'],
            "answer": res['_source']['answer'],
        }
        for res in response["hits"]['hits']
    ]
    print("Response:")
    pprint(response[0]['answer'])


def main():
    query_list = [
        "明天去相亲",
        "我放了个屁，表扬我",
        "明天要考试",
        "考试考砸了",
        "没赶上火车，难受",
        "钱包丢了",
        "我真的不想活了，找不到工作",
        "夸我",
        "求夸",
        "妈妈说我长得丑，求夸",
        "曹政放了个屁，真臭",
        "下周二部门聚餐",
        "对火锅的期望",
        "你是傻逼"
    ]
    for query in query_list:
        query = query_preprocessing(query)
        request_query(query)



if __name__ == '__main__':
    # Creates ES client
    client = Elasticsearch(hosts=["127.0.0.1"])
    main()