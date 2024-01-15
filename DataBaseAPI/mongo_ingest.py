import json
from pymongo.mongo_client import MongoClient

############################################################################################################

PATH = 'files/'

# Creacion de la conexión a la base de datos (cloud)
user = "jorge_47"
password = "JstJgJrDTa1yaCnI"
ip = "0.0.0.0/0"
uri = "mongodb+srv://" + user + ":" + password + "@cluster0.7fsauam.mongodb.net/?retryWrites=true&w=majority"
# 1) Create a new client and connect to the cloud MongoDB instance (remoto)
# client = MongoClient(uri, server_api=ServerApi('1'))

# 2) Create a new client and connect to the cloud MongoDB instance (local)
client = MongoClient(host="localhost", port=27017)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['tpfinal']  # Crea el esquema de la base de datos

users_collection = db['users']
# print(cb_products)
users_collection.drop()
with open(PATH + 'users.json') as f:
    d = json.load(f)
    # pprint(d[0:1]) # print just a sample with the first 3 elements
    users_collection.insert_many(d)

print(client.list_database_names())
print("Done.")
client.close()
