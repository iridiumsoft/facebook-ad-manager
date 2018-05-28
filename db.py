import os
from dotenv import load_dotenv
from pymongo import MongoClient
import time

load_dotenv('.env')

client = MongoClient(host='localhost', port=int(os.getenv("DATABASE_PORT")))
db = client[os.getenv("DATABASE_NAME")]
