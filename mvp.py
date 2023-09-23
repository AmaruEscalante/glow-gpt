from open_ai import PromptBuilder, OpenAIChat, SalesPitchBuilder, Embedding
from entities import Message
from db_client import DBClient
from vector_db import LongTermMemoryService
import csv
# formatted_messages = PromptBuilder.get_formatted_input(messages)
# response = OpenAIChat.get_response(formatted_messages)

mongo_client = DBClient()

mongo_client.delete_messsages_with_phone_number("51970748423")

while True:
    input_message = input("Usuario: ")
    query_embedding = Embedding.encode(input_message)
    response = LongTermMemoryService.retrieve(input_message)
    id_matches = [match['id'] for match in response['matches']]
    print(id_matches)
    sales_pitch = mongo_client.retrieve_sales_pitches_with_cod_saps(id_matches)
    print("Related sales pitches", sales_pitch)
    new_message = Message("51970748423", input_message, False)
    mongo_client.upsert_message(new_message)
    messages = mongo_client.retrieve_messages_with_phone_number("51970748423")
    formatted_messages = PromptBuilder.get_formatted_input(messages, extra_context=sales_pitch)
    response = OpenAIChat.get_response(formatted_messages)
    print("GlowGPT: ", response)
    mongo_client.upsert_message(Message("51970748423", response, True))