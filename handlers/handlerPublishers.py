import tornado, asyncio, json
from pymongo import AsyncMongoClient
from bson import ObjectId

class PublisherHandler(tornado.web.RequestHandler):
    def initialize(self):
        #Connessione al Database MongoDB
        self.client = AsyncMongoClient("mongodb://localhost:27017")

        #Recupero e selezione del db e delle collezioni
        self.db = self.client["bp_database"]
        self.bookCollection = self.db["books"]
        self.pubCollection = self.db["publishers"]
    
    async def get(self, publisher_id = None):
        self.set_header("Content-Type", "application/json")
        
        pubName = self.get_argument("name", None)
        pubCountry = self.get_argument("country", None)
                
        if publisher_id:
            try:
                doc = await self.pubCollection.find_one({"_id": ObjectId(publisher_id)})
                doc["_id"] = str(doc['_id'])
                
                self.set_status(200)
                self.write(doc)
            except Exception as e:
                self.set_status(400)
                self.write({"error": str(e)})
            
        elif not publisher_id:
            respDict = []
            
            coll_curs = self.pubCollection.find({})
            async for doc in coll_curs:
                doc["_id"] = str(doc['_id'])
                respDict.append(doc)
            
            self.set_status(200)
            self.write(tornado.escape.json_encode({
                "publishers": respDict
            }))