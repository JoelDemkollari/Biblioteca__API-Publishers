import tornado, asyncio, json, logging
from pymongo import AsyncMongoClient

logging.basicConfig(level=logging.DEBUG)

async def main():
    #Connessione al Database MongoDB
    client = AsyncMongoClient("mongodb://localhost:27017")

    #Recupero e selezione del db e delle collezioni
    db = client["bp_database"]
    bookCollection = db["books"]
    pubCollection = db["publishers"] 
    
    #Recupero dei dati publisher e books dai file json
    with open(file="fileTemporanei/pubData.json") as p:
        datiPubs = json.load(p)
        
    with open(file="fileTemporanei/bookData.json") as b:
        datiLibri = json.load(b)
    
    #Inserimento asincrono al database dei dati publishers
    await pubCollection.insert_many(datiPubs)
    
    #Inserimento asincrono al database dei dati books
    try:
        #Per ogni libro andiamo a recuperare la casa editrice
        for libro in datiLibri:
            doc_id = await pubCollection.find_one({"name": libro['publisher_id']})
            
            #Modifichiamo direttamente la proprieta 'publisher_id'
            #Sostituendo il nome della casa editrice con il suo ObjectId creato in precedenza da mongodb
            libro["publisher_id"] = doc_id['_id']
            
            #Lo inseriamo nella collezione books
            await bookCollection.insert_one(libro)
        
        logging.debug("Caricamento Dati eseguito con Successo.")
    #In caso di qualche errore
    except Exception as e:
        #Stampo sia un messaggio di errore che l'errore stesso
        logging.debug("Errore nel caricamento dei dati nel database:")
        logging.debug(e)

if __name__ == "__main__":
    asyncio.run(main())