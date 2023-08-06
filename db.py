# db.py
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

is_production = os.getenv("NODE_ENV") == "production"
db_user = os.getenv("DB_USER_PROD" if is_production else "DB_USER_DEV")
db_pass = os.getenv("DB_PASS_PROD" if is_production else "DB_PASS_DEV")
db_host = os.getenv("DB_HOST_PROD" if is_production else "DB_HOST_DEV")
db_database = os.getenv("DB_DATABASE_PROD" if is_production else "DB_DATABASE_DEV")

mongo_uri = f"mongodb+srv://{db_user}:{db_pass}@{db_host}/{db_database}?retryWrites=true&w=majority"

client = MongoClient(mongo_uri)
db = client.get_database()
collection = db.list_numbers  # Replace 'your_collection_name' with your actual collection name
collection_main = db.main_numbers  # Replace 'your_collection_name' with your actual collection name

print("Conectado com Sucesso!")
