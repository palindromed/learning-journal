import os
import requests
import json
import io
from learning_journal.models import DBSession, Post, Base
from sqlalchemy import create_engine
import transaction


def request_posts():
    key = os.environ.get('JOURNAL_API', '')
    response = requests.get('https://sea401d2.crisewing.com/api/export?apikey=' + key)
    response.raise_for_status()
    return response.text


def read_posts():
    with io.open('response.json', 'r') as file:
        saved_json = file.read()
    return saved_json


def sift_for_post_json(json_load):
    sifted_posts = []
    for item in json_load:
        post = {
            "title": item["title"],
            "text": item["text"],
            "created": item["created"],
        }
        sifted_posts.append(post)
    return sifted_posts


def populate_db(json_for_post):
    post = Post(**json_for_post)
    DBSession.add(post)
    DBSession.flush()


def get_posts():
    http_response_text = request_posts()
    json_load = json.loads(http_response_text)
    return sift_for_post_json(json_load)


def main():
    database_url = os.environ.get("DATABASE_URL", None)
    engine = create_engine(database_url)
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        for post in get_posts():
            populate_db(post)


if __name__ == '__main__':
    main()
