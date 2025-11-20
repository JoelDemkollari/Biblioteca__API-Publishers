import tornado, asyncio, json
from pymongo import AsyncMongoClient

class BookHandler(tornado.web.RequestHandler):
    
    def get(self, book_id = None):
        print(book_id)