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
df = pd.read_csv('products_curated_updated.csv')  # Asegúrate de que la ruta al archivo CSV sea correcta

# Crear un nuevo DataFrame para almacenar los resultados
sales_pitch_df = pd.DataFrame(columns=['codsap', 'sales_pitch'])

# Iterar sobre las filas del DataFrame original
for index, row in df.iterrows():
    # Extraer los valores de las columnas específicas y asignarlas a variables
    cod = row['codsap']
    product = row['desproducto']
    group = row['desunidadnegocio']
    brand = row['desmarca']
    category = row['descategoria']
    
    # Obtener el sales pitch y la respuesta
    formatted_messages = SalesPitchBuilder.get_sales_pitch(product, group, category, brand)
    response = OpenAIChat.get_response(formatted_messages)
    
    # Añadir una nueva fila al DataFrame de sales_pitch
    sales_pitch_df = sales_pitch_df.append({'codsap': cod, 'sales_pitch': response}, ignore_index=True)

# Guardar el DataFrame de sales_pitch en un nuevo archivo CSV
sales_pitch_df.to_csv('sales_pitch.csv', index=False, encoding='utf-8-sig')
