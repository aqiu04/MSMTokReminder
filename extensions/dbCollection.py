from pymongo import MongoClient

class dbCollection():
    def __init__(self, collection):
        CONNECTION_STRING = "mongodb+srv://testuser:TestTest@dailyword1.2fxp7z3.mongodb.net/"
        client = MongoClient(CONNECTION_STRING)

        self.collection = client['DailyWords'][collection]

    def find_in_db(self, query, search_term = "_id"):
        thing = self.collection.find_one({search_term: query.lower()})
        return thing != None
    
    def fetch_from_db(self, query, search_term = "_id"):
        return self.collection.find_one({search_term: query.lower()})

    def fetch_all_from_db(self):
        return self.collection.find({})
        
    def store_in_db(self, id, value):
        element = {
            "_id" : id.lower(),
            "data" : value
        }

        self.collection.insert_one(element)
        
    def replace_in_db(self, id, value) -> bool:
        if not self.find_in_db(id):
            return False
        old_element = self.fetch_from_db(id)
        new_element = {
            "_id" : id.lower(),
            "data" : value
        }
        self.collection.replace_one(old_element, new_element)
        return True
    
    def delete_from_db(self, id) -> bool:
        if not self.find_in_db(id):
            return False
        element = {
            "_id" : id.lower()
        }
        self.collection.delete_one(element)
        return True

    
    