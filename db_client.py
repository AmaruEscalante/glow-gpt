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

    
    def upsert_sales_pitch(self, cod_sap: str, sales_pitch: str):
        db = self.client.belcorp
        collection = db.sales_pitch
        result = collection.insert_one(
            {
                "cod_sap": cod_sap,
                "sales_pitch": sales_pitch,
            }
        )
        print(result)

    def retrieve_sales_pitches_with_cod_saps(self, cod_saps: List[str]) -> List[str]:
        db = self.client.belcorp
        collection = db.sales_pitch
        documents = collection.find({"cod_sap": {"$in": cod_saps}})

        sales_pitches = [doc["sales_pitch"] for doc in documents]

        return sales_pitches
    
    def retrieve_products_with_cod_saps(self, cod_saps: List[str]) -> List[str]:
        db = self.client.belcorp
        collection = db.products
        documents = collection.find({"cod_sap": {"$in": cod_saps}})
        products = [
            {
                "cod_sap": doc["cod_sap"],
                "name": doc["name"],
            } for doc in documents
        ]
        return products

    def upsert_product(self, cod_sap: str, name: str):
        db = self.client.belcorp
        collection = db.products
        result = collection.insert_one(
            {
                "cod_sap": cod_sap,
                "name": name,
            }
        )
        print(result)

    def upsert_recommendations(self, phone_number: str, recommendations: List[str]):
        db = self.client.belcorp
        collection = db.recommendations
        documents = [{"phone_number": phone_number, "cod_sap": recommendation["cod_sap"]} for recommendation in recommendations]
        if len(documents) > 0:
            result = collection.insert_many(documents)
            print(result)

    def retrieve_recommendations(self, phone_number: str) -> List[str]:
        db = self.client.belcorp
        collection = db.recommendations
        documents = collection.find({"phone_number": phone_number})
        recommendations = [doc["cod_sap"] for doc in documents]
        return recommendations
    

    def retrieve_recommendations_and_sales_pitch(self, phone_number: str) -> List[dict]:
        db = self.client.belcorp
        collection = db.recommendations
        documents = collection.find({"phone_number": phone_number})
        recommendations = [doc["cod_sap"] for doc in documents]
        catalogue_body = []
        for cod_sap in recommendations:
            catalogue_body.append({
                "cod_sap": cod_sap,
                "sales_pitch": self.retrieve_sales_pitches_with_cod_saps([cod_sap])[0],
            })
        return catalogue_body
    
    def delete_recommendations(self, phone_number: str):
        db = self.client.belcorp
        collection = db.recommendations
        collection.delete_many({"phone_number": phone_number})