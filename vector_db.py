import pinecone
import settings
from open_ai import Embedding

class LongTermMemoryService:
    api_key = settings.PINECONE_API_KEY
    environment = settings.PINECONE_ENV

    @staticmethod
    def list_indexes():
        pinecone.init(
            api_key=LongTermMemoryService.api_key,
            environment=LongTermMemoryService.environment,
        )
        return pinecone.list_indexes()

    @staticmethod
    def retrieve(query: str, index='belcorp') -> str:
        pinecone.init(
            api_key=LongTermMemoryService.api_key,
            environment=LongTermMemoryService.environment,
        )
        
        try:
            vector = Embedding.encode(query)
            pinecone_index = pinecone.Index(index)
            response = pinecone_index.query(
                vector=vector,
                top_k=3,
                include_values=True,
            )
            return response
        except Exception as e:
            print(f"Error al buscar en la base de datos\nError: {str(e)}")

    @staticmethod
    def upsert_data(cod_embeddings, index='belcorp'):
        pinecone.init(
            api_key=settings.PINECONE_API_KEY, 
            environment=settings.PINECONE_ENV, 
        )
        try:
            pinecone_index = pinecone.Index(index)
            pinecone_index.upsert(vectors=cod_embeddings)
            print("upserting")
        except Exception as e:
            print("Error al insertar en la base de datos", str(e))

    @staticmethod
    def delete_data():
        pinecone.init(
            api_key=settings.PINECONE_API_KEY, 
            environment=settings.PINECONE_ENV, 
        )

        try:
            pinecone_index = pinecone.Index("belcorp")
            delete_response = pinecone_index.delete(delete_all=True)
            print("Deleted all vectors")
            return delete_response
        except Exception as e:
            print("Error al eliminar en la base de datos")