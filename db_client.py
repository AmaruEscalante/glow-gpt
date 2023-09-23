from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from entities import Message
from typing import List
import settings

class DBClient:
    def __init__(self):
        self.uri = f"mongodb+srv://noam:{settings.MONGODB_PASSWORD}@noamcluster.4zesjit.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        # Recuerda añadir tu ip
        
        # Verifica la conexión
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def upsert_message(self, message: Message):
        db = self.client.belcorp
        collection = db.messages
        result = collection.insert_one(
            {
                "phone_number": message.phone_number,
                "content": message.content,
                "from_assistant": message.is_from_assistant,
            }
        )
        print(result)

    def retrieve_messages_with_phone_number(self, phone_number: str) -> List[Message]:
        db = self.client.belcorp
        collection = db.messages
        documents = collection.find({"phone_number": phone_number})

        messages = [
            Message(
                phone_number=doc["phone_number"],
                content=doc["content"],
                is_from_assistant=doc["from_assistant"],
            )
            for doc in documents
        ]

        return messages
    
    def delete_messsages_with_phone_number(self, phone_number: str):
        db = self.client.belcorp
        collection = db.messages
        collection.delete_many({"phone_number": phone_number})