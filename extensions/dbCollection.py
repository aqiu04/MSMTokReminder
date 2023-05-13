from pymongo import MongoClient

class dbCollection():
    def __init__(self, collection):
        CONNECTION_STRING = "mongodb+srv://testuser:TestTest@dailyword1.2fxp7z3.mongodb.net/"
        client = MongoClient(CONNECTION_STRING)

        self.collection = client['DailyWords'][collection]

    def find_in_db(self, query):
        thing = self.collection.find_one({"_id" : query.lower()})
        return thing != None
    
    def fetch_from_db(self, query):
        return self.collection.find_one({"_id" : query.lower()})
        
    def store_in_db(self, id, value):
        element = {
            "_id" : id.lower(),
            "data" : value
        }

        self.collection.insert_one(element)


    
    