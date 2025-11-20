import tornado, asyncio, json
from pymongo import AsyncMongoClient

class PublisherHandler(tornado.web.RequestHandler):

    def get(self, publisher_id = None):
        print(publisher_id)