import os
from dotenv import load_dotenv

# Carga las variables de entorno desde .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")