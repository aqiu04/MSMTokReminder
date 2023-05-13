from pymongo import MongoClient

class dbCollection():
    def __init__(self, collection):
        CONNECTION_STRING = "mongodb+srv://testuser:TestTest@dailyword1.2fxp7z3.mongodb.net/"
        client = MongoClient(CONNECTION_STRING)

        self.db = client['DailyWords']
        self.collection = self.db[collection]

    def find_in_db(query):
        thing = self.collection.find_one({"_id" : query})
        return thing != None
    
    def fetch_from_db(self, query):
        return self.collection.find_one({"_id" : query})
        
    def store_in_db(self, id, value):
        element = {
            "_id" : id,
            "data" : value
        }

        self.collection.insert_one(element)


    
    