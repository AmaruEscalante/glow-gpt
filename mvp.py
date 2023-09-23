from open_ai import PromptBuilder, OpenAIChat, SalesPitchBuilder, Embedding
from entities import Message
from db_client import DBClient
from vector_db import LongTermMemoryService
import csv 

def process_text_message_from_phone_number(text_message: str, phone_number: str):
    mongo_client = DBClient()
    response = LongTermMemoryService.retrieve(text_message)
    id_matches = [match['id'] for match in response['matches']]
    print(id_matches)
    sales_pitch = mongo_client.retrieve_sales_pitches_with_cod_saps(id_matches)
    new_message = Message(phone_number, text_message, False)
    mongo_client.upsert_message(new_message)
    messages = mongo_client.retrieve_messages_with_phone_number(phone_number)
    formatted_messages = PromptBuilder.get_formatted_input(messages, extra_context=sales_pitch)
    response = OpenAIChat.get_response(formatted_messages)
    mongo_client.upsert_message(Message(phone_number, response, True))
    products = mongo_client.retrieve_products_with_cod_saps(id_matches)
    recommendations = []
    for product in products:
        if product["name"].lower() in response.lower():
            recommendations.append(product)
    mongo_client.upsert_recommendations(phone_number, recommendations)
    return response

def retrieve_recommendations_for_catalogue(phone_number: str):
    mongo_client = DBClient()    
    catalogue_body = mongo_client.retrieve_recommendations_and_sales_pitch(phone_number)
    return catalogue_body

def restart_recommendations_for_number(phone_number: str):
    mongo_client = DBClient()
    mongo_client.delete_recommendations(phone_number)


mongo_client = DBClient()
mongo_client.delete_messsages_with_phone_number("51987501744")