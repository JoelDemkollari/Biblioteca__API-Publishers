import tornado, asyncio, json
from pymongo import AsyncMongoClient
from bson import ObjectId

class BookHandler(tornado.web.RequestHandler):
    def initialize(self):
        #Connessione al Database MongoDB
        self.client = AsyncMongoClient("mongodb://localhost:27017")

        #Recupero e selezione del db e delle collezioni
        self.db = self.client["bp_database"]
        self.bookCollection = self.db["books"]
        self.pubCollection = self.db["publishers"]
    
    async def get(self, publisher_id, book_id = None):
        self.set_header("Content-Type", "application/json")
        
        title = self.get_argument("title", None)
        author = self.get_argument("author", None)
        genere = self.get_argument("genre", None)
        
        if not publisher_id:
            self.set_status(400)
            self.write({"error": "no publisher id given"})
            return
                
        publisher_obj = await self.pubCollection.find_one({"_id": ObjectId(publisher_id)})
        
        if not publisher_obj:
            self.set_status(400)
            self.write({"error": "invalid publisher_id given"})
            return

        query = {}
        query["publisher_id"] = ObjectId(publisher_id)
        
        if title:
            query["title"] = title
        if author:
            query["author"] = author
        if genere:
            query["genre"] = genere
        
        respDict = []
        coll_curs = self.bookCollection.find(query)
        async for doc in coll_curs:
            doc["_id"] = str(doc['_id'])
            doc["publisher_id"] = str(doc["publisher_id"])
            respDict.append(doc)
            
        self.set_status(200)
        self.write(tornado.escape.json_encode({
            str(publisher_id): respDict
        }))
    
    async def post(self, publisher_id):
        self.set_header("Content-Type", "application/json")
        
        data = tornado.escape.json_decode(self.request.body)
        data_keys = set(data.keys())
        
        if not publisher_id:
            self.set_status(400)
            self.write({"error": "no publisher id given"})
            return
                
        publisher_obj = await self.pubCollection.find_one({"_id": ObjectId(publisher_id)})
        
        if not publisher_obj:
            self.set_status(400)
            self.write({"error": "invalid publisher_id given"})
            return
        
        req_fields = {"title", "author", "genre", "year"}

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
        
        data["publisher_id"] = ObjectId(publisher_id)
        
        try:
            await self.bookCollection.insert_one(data)
            self.set_status(200)
        except Exception as e:
            self.set_status(400)
            self.write({"error": str(e)})
    
    async def put(self, publisher_id, book_id):
        self.set_header("Content-Type", "application/json")
        
        data = tornado.escape.json_decode(self.request.body)
        data_keys = set(data.keys())
        
        #CONTROLLO DEL PUBLISHER ID
        if not publisher_id:
            self.set_status(400)
            self.write({"error": "no publisher id given"})
            return
                
        publisher_obj = await self.pubCollection.find_one({"_id": ObjectId(publisher_id)})
        
        if not publisher_obj:
            self.set_status(400)
            self.write({"error": "invalid publisher_id given"})
            return
        
        #CONTROLLO DEL BOOK ID
        if not book_id:
            self.set_status(400)
            self.write({"error": "no book id given"})
            return
                
        book_obj = await self.bookCollection.find_one({"_id": ObjectId(book_id)})
        
        if not book_obj:
            self.set_status(400)
            self.write({"error": "invalid book_id given"})
            return
        
        #CONTROLLO DELLA CORRETTEZZA DEI VARI PARAMETRI FORNITI
        req_fields = {"title", "author", "genre", "year"}

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
        
        #AGGIORNAMENTO
        update_doc = {param: data[param] for param in data}
            
        for param in data:
            await self.pubCollection.update_one({"_id": ObjectId(book_id)}, {"$set": update_doc})
            self.set_status(200)
        
    async def delete(self, publisher_id, book_id):
        self.set_header("Content-Type", "application/json")
        
        #CONTROLLO DEL PUBLISHER ID
        if not publisher_id:
            self.set_status(400)
            self.write({"error": "no publisher id given"})
            return
                
        publisher_obj = await self.pubCollection.find_one({"_id": ObjectId(publisher_id)})
        
        if not publisher_obj:
            self.set_status(400)
            self.write({"error": "invalid publisher_id given"})
            return
        
        #CONTROLLO DEL BOOK ID
        if not book_id:
            self.set_status(400)
            self.write({"error": "no book id given"})
            return
                
        book_obj = await self.bookCollection.find_one({"_id": ObjectId(book_id)})
        
        if not book_obj:
            self.set_status(400)
            self.write({"error": "invalid book_id given"})
            return
        
        try:
            await self.bookCollection.delete_one({"_id": book_id})
            self.set_status(200)
        except Exception as e:
            self.set_status(400)
            self.write({"error": str(e)})