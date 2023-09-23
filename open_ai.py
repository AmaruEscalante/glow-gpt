import openai
from entities import Message
from typing import List
from settings import OPENAI_API_KEY

class Embedding:
    @staticmethod
    def encode(query: str):
        openai.api_key = OPENAI_API_KEY
        query = query.replace("\n", " ")
        return openai.Embedding.create(input = [query], model="text-embedding-ada-002")['data'][0]['embedding']

class OpenAIChat:
    @staticmethod
    def get_response(formatted_messages: List[dict]):
        # Aun podría haber tests con los parametros
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=formatted_messages,
            temperature=0.9,
            max_tokens=256,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )
        return response['choices'][0]['message']['content']

prompt = """
Tu nombre es GlowGPT. Eres un asistente virtual de belleza que acompaña a mujeres en su proceso de compra.
El objetivo de GlowGPT es ayudar a las mujeres a encontrar los productos de belleza que mejor se adapten a sus necesidades.
Tienes acceso a un catálogo de productos de belleza de la empresa Belcorp.
Considera la información del catálogo de ser necesario para responder.

Catálogo:
{catalogue}
"""

class PromptBuilder:
    
    @staticmethod
    def get_formatted_input(list_of_messages: List[Message], extra_context: List[str]) -> List[dict]:
        formatted_messages = []

        local_prompt = prompt.format(catalogue="\n".join(extra_context))

        formatted_messages.append({"role": "system", "content": local_prompt})

        for message in list_of_messages:
            if message.is_from_assistant:
                new_element = {"role": "assistant", "content": message.content}
            else:
                new_element = {"role": "user", "content": message.content}
            formatted_messages.append(new_element)
        return formatted_messages
    
sales_pitch_prompt = """
Genera un pitch de ventas para un producto de belleza. El pitch debe incluir para qué sirve y que contenga palabras clave relevantes para facilitar su búsqueda.
Nombre: {NAME}
Grupo: {GROUP}
Categoría: {CATEGORY}
Marca: {BRAND}. {BRAND_DESCRIPTION}  

EJEMPLO 1:
INPUT:
Nombre: LB SATIN NUDE PERF 50ML
Grupo: Fragancias
Categoría: Cosméticos
Marca: LBEL. Buscamos inspirar a cada mujer a revelar su belleza única para destacar con estilo propio. Es la marca premium del portafolio.
OUTPUT:
💄 ¡Revela tu belleza única con LB Satin Nude Perf 50ML! 💄
Nombre: LB SATIN NUDE PERF 50ML. Una fragancia elegante y sutil, creada para la mujer sofisticada que busca destacar su estilo propio con un aroma inconfundible.
Uso: Ideal para eventos formales, cenas elegantes o simplemente para sentirte empoderada y hermosa en tu día a día, LB Satin Nude es la elección perfecta para mujeres que buscan un aroma distintivo y duradero.
Palabras clave: LB Satin Nude, Fragancias, Cosméticos, LBEL, Belleza Única, Estilo Propio, Marca Premium, Elegancia, Sofisticación, Glamour, Refinamiento, Mujer Sofisticada.

EJEMPLO 2:
INPUT:
Nombre: CZ SANDIA SHAKE COL CC 200 ML
Grupo: Fragancias
Categoría: Cosméticos
Marca: Cyzone. Cyzone es una marca de belleza accesible de alta calidad para todas las mujeres jóvenes de Latinoamérica que aman compartir a través de la belleza, que les gusta experimentar y estar a la vanguardia con las últimas tendencias.
OUTPUT:
🌺 ¡Refresca tu estilo con CZ Sandia Shake Col CC 200 ML! 🌺
Nombre: CZ SANDIA SHAKE COL CC 200 ML. Una fragancia vibrante y juguetona que encapsula la frescura de la sandía, diseñada para mujeres jóvenes que buscan un aroma distintivo y revitalizante.
Uso: Perfecta para cualquier ocasión, ya sea un día en la oficina o una noche en la ciudad, esta fragancia es tu compañera ideal, proporcionando un aroma fresco y duradero.
Palabras clave: CZ Sandia Shake, Fragancias, Cosméticos, Cyzone, Belleza Accesible, Alta Calidad, Mujeres Jóvenes, Latinoamérica, Frescura, Revitalizante, Tendencias.
"""

brand_description = {
    "CYZONE": "Cyzone es una marca de belleza accesible de alta calidad para todas las mujeres jóvenes de Latinoamérica que aman compartir a través de la belleza, que les gusta experimentar y estar a la vanguardia con las últimas tendencias.",
    "ESIKA": "Esika es una marca con historia y una de las favoritas en la categoría de belleza. Es la marca de entrada del portafolio. Su frase es millones de mujeres eligen Esika.",
    "LBEL": "Lbel. Buscamos inspirar a cada mujer a revelar su belleza única para destacar con estilo propio. Es la marca premium del portafolio.",
}

class SalesPitchBuilder:
    @staticmethod
    def get_sales_pitch(product_name: str, group: str, category: str, brand: str):
        formatted_messages = []

        sales_pitch_prompt_local = sales_pitch_prompt.format(NAME=product_name, GROUP=group, CATEGORY=category, BRAND=brand, BRAND_DESCRIPTION=brand_description[brand])

        formatted_messages.append({"role": "system", "content": sales_pitch_prompt_local})

        return formatted_messages