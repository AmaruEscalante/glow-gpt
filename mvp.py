from open_ai import PromptBuilder, OpenAIChat, SalesPitchBuilder
from entities import Message
from db_client import DBClient

# formatted_messages = PromptBuilder.get_formatted_input(messages)
# response = OpenAIChat.get_response(formatted_messages)
"""
mongo_client = DBClient()

while True:
    input_message = input("Usuario: ")
    new_message = Message("51970748423", input_message, False)
    mongo_client.upsert_message(new_message)
    messages = mongo_client.retrieve_messages_with_phone_number("51970748423")
    formatted_messages = PromptBuilder.get_formatted_input(messages)
    response = OpenAIChat.get_response(formatted_messages)
    print("GlowGPT: ", response)
    mongo_client.upsert_message(Message("51970748423", response, True))
"""

import pandas as pd

# Leer el archivo CSV
df = pd.read_csv('products_curated.csv')  # Asegúrate de que la ruta al archivo CSV sea correcta

# Iterar sobre las filas del DataFrame
for index, row in df.iterrows():
    # Extraer los valores de las columnas específicas y asignarlas a variables
    cod = row['codsap']
    product = row['desproducto']
    group = row['desunidadnegocio']
    brand = row['desmarca']
    category = row['descategoria']
    
    # Aquí puedes hacer lo que necesites con las variables
    print(cod, product, group, brand, category)
    formatted_messages = SalesPitchBuilder.get_sales_pitch(product, group, category, brand)
    response = OpenAIChat.get_response(formatted_messages)
    print(response)