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
        
        #Recupero filtri nel caso in cui ci siano
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
            
            query = {}
            if pubName:
                query["name"] = pubName
            if pubCountry:
                query["country"] = pubCountry
            
            if pubCountry or pubName:
                coll_curs = self.pubCollection.find(query)
            else:            
                coll_curs = self.pubCollection.find({})
            async for doc in coll_curs:
                doc["_id"] = str(doc['_id'])
                respDict.append(doc)
            
            self.set_status(200)
            self.write(tornado.escape.json_encode({
                "publishers": respDict
            }))
    
    async def post(self):
        self.set_header("Content-Type", "application/json")
        
        data = tornado.escape.json_decode(self.request.body)
        data_keys = set(data.keys())
        
        req_fields = {"name", "founded_year", "country"}

        mancanti = req_fields - data_keys
        extra = data_keys - req_fields
        
        if mancanti:
            self.set_status(400)
            self.write({"error": f"Missing required parameters: {', '.join(mancanti)}"})
            return
        
        if extra:
            self.set_status(400)
            self.write({"error": f"Unexpected parameters found: {', '.join(extra)}"})
            return

        try:
            await self.pubCollection.insert_one(data)
            self.set_status(200)
        except Exception as e:
            self.set_status(400)
            self.write({"error": str(e)})
            
    async def put(self, publisher_id = None):
        self.set_header("Content-Type", "application/json")
        
        data = tornado.escape.json_decode(self.request.body)
                
        req_fields = {"name", "founded_year", "country"}

        extra = set(data.keys()) - req_fields
        
        if extra:
            self.set_status(400)
            self.write({"error": f"Unexpected parameters found: {', '.join(extra)}"})
            return
        
        if publisher_id:                        
            update_doc = {param: data[param] for param in data}
            
            for param in data:
                await self.pubCollection.update_one({"_id": ObjectId(publisher_id)}, {"$set": update_doc})
                self.set_status(200)
                
    async def delete(self, publisher_id = None):
        self.set_header("Content-Type", "application/json")
        
        if publisher_id:
            try:
                await self.pubCollection.delete_one({"_id": ObjectId(publisher_id)})
        
                await self.bookCollection.delete_many({"publisher_id": ObjectId(publisher_id)})
                
                self.set_status(200)
            except Exception as e:
                self.set_status(400)
                self.write({"error": str(e)})
        else:
            self.set_status(500)
            self.write({"error": "no publisher id given"})
            return