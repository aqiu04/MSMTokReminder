from pymongo import MongoClient

def get_database(name):
 
   CONNECTION_STRING = "mongodb+srv://testuser:TestTest@dailyword1.2fxp7z3.mongodb.net/"
 
   client = MongoClient(CONNECTION_STRING)
 
   # returns the database with the given name
   return client[name]
