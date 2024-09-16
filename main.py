import random
import string
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(hosts=["http://localhost:9200"])

# Index name
INDEX_NAME = 'documents'

# Delete the index if it exists
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)

# Create the index with mapping
mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "creation_date": {"type": "date"},
            "update_date": {"type": "date"}
        }
    }
}
es.indices.create(index=INDEX_NAME, body=mapping)

# Generate 100 documents
for i in range(10):
    title = 'amrita'
    content = ''.join(random.choices(string.ascii_lowercase + string.digits, k=50))
    # Random creation date within the last 100 days
    creation_date = datetime.now() - timedelta(days=random.randint(0, 100))
    update_date = creation_date + timedelta(days=random.randint(0, 100))
    doc = {
        'title': title,
        'content': content,
        'creation_date': creation_date,
        'update_date': update_date
    }
    print(f'document {title} and {content} and {creation_date} and {update_date}')
    es.index(index=INDEX_NAME, body=doc)

# Refresh the index
es.indices.refresh(index=INDEX_NAME)

# Search Functionality
def search_documents(query):
    search_body = {
        "query": {
            "function_score": {
                "query": {
                    "match_all": {}
                },
                "functions": [
                    {
                        "exp": {
                            "creation_date": {
                                "origin": "now",
                                "scale": "30d",
                                "decay": 0.5
                            }
                        }
                    }
                ],
                "boost_mode": "multiply"
            }
        }
   }
    # search_body = {
    #     "query": {
    #         "multi_match": {
    #             "query": query,
    #             "fields": ["title", "content", "creation_date", "update_date"]
    #         }
    #     },
    #     "sort": [
    #         {"creation_date": {"order": "desc"}}
    #     ]
    # }
    import pdb
    pdb.set_trace()
    res = es.search(index=INDEX_NAME, body=search_body)
    for hit in res['hits']['hits']:
        print(f"titli: Score: {hit['_score']}, Creation Date: {hit['_source']['creation_date']}, Update Date: {hit['_source']['update_date']}")

# Example search
if __name__ == "__main__":
    query = input("Enter search query: ")
    search_documents(query)


