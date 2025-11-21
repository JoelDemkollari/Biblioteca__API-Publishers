import tornado, asyncio
from pymongo import AsyncMongoClient
from handlers import handlerBooks, handlerPublishers

def make_app():
    return tornado.web.Application([
        (r"/publishers", handlerPublishers.PublisherHandler),
        (r"/publishers/([a-f0-9]{24})", handlerPublishers.PublisherHandler)
    ])

async def main(shutdown_event):
    app = make_app()
    app.listen(8888)
    await shutdown_event.wait()
    print("Shutdown ricevuto, chiusura server...")

if __name__ == "__main__":
    client = AsyncMongoClient("mongodb://localhost:27017")
    
    db = client["bp_database"]
    book_collection = db["books"]
    pub_collection = db["publishers"]
    
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()